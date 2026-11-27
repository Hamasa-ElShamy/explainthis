import pathlib, subprocess, sys, time, threading, shutil, pytest
from explainthis import engine, kb, cli

S = pathlib.Path(__file__).parent / "samples"
# Samples captured from real runs (python/git/bash/npm/network). These were typed from the exact
# messages Windows/Git/pip print, because this test machine is Linux: win-*, firewall-off,
# git-push-rejected, git-conflict, py-pip-managed, disk-full, oom.
TYPED = {"win-smartscreen", "win-uac", "win-dll", "win-access-denied", "firewall-off", "git-push-rejected", "git-conflict", "py-pip-managed", "disk-full", "oom"}
EXPECT = {"disk-full": "disk-full", "oom": "oom", "npm-err": "npm-err"}

def first(name):
    return engine.explain((S / f"{name}.txt").read_text())["matches"]

@pytest.mark.parametrize("name", sorted(p.stem for p in S.glob("*.txt")))
def test_sample_gets_expected_explanation(name):
    m = first(name)
    want = EXPECT.get(name, name)
    assert m, f"no explanation for {name}"
    assert want in [x["id"] for x in m], (name, [x["id"] for x in m])

def test_every_kb_entry_has_a_sample():
    have = {p.stem for p in S.glob("*.txt")}
    assert {e["id"] for e in kb.E} <= have

def test_every_entry_has_arabic_and_english():
    for e in kb.E:
        for k in ("title", "mean", "steps"):
            assert len(e[k]) == 2 and e[k][0] and e[k][1], (e["id"], k)
        assert len(e["steps"][0]) == len(e["steps"][1]), e["id"]

def test_location_and_code_line():
    r = engine.explain((S / "oom.txt").read_text())
    assert r["where"]["file"] == "train.py" and r["where"]["line"] == "9" and "10**12" in r["where"]["code"]

def test_module_name_mapping():
    t = engine.render("ModuleNotFoundError: No module named 'sklearn.linear_model'")
    assert "scikit-learn" in t

def test_risky_actions_get_consequence_and_risk():
    t = engine.render((S / "win-smartscreen.txt").read_text())
    assert "Risk: High" in t and "Run anyway" in t and "never clicks" in t
    assert "exposed to unauthorized" in engine.render("turn off the firewall")

def test_unknown_message_is_honest():
    t = engine.render("Error: flux capacitor desynchronised (code ZZ-91)")
    assert "do not have a built-in explanation" in t and "does not guess" in t and "ZZ-91" in t

def test_arabic():
    t = engine.render((S / "py-module.txt").read_text(), "ar")
    assert "بايثون مش لاقي المكتبة" in t and "ممكن تعمل إيه" in t

def test_run_explains_automatically_on_failure(tmp_path, capsys):
    f = tmp_path / "bad.py"; f.write_text("d = {}\nd['x']\n")
    code = cli.run_cmd([sys.executable, str(f)], "en")
    out = capsys.readouterr().out
    assert code == 1 and "KeyError" in out and "ExplainThis: the command exited with code 1" in out and f"{f}:2" in out

def test_run_stays_silent_on_success(capsys):
    assert cli.run_cmd([sys.executable, "-c", "print('hi')"], "en") == 0
    assert "ExplainThis" not in capsys.readouterr().out

def test_watch_explains_new_error_block(tmp_path, capsys):
    log = tmp_path / "app.log"; log.write_text("")
    t = threading.Thread(target=cli.watch, args=(str(log), "en", 0.4), daemon=True); t.start()
    time.sleep(0.5)
    with open(log, "a") as f:
        f.write("INFO started\n"); f.flush()
        f.write("Traceback (most recent call last):\n  File \"app.py\", line 3, in <module>\n    x = d['k']\nKeyError: 'k'\n"); f.flush()
    time.sleep(1.5)
    out = capsys.readouterr().out
    assert "KeyError: the key 'k' is not in the dictionary" in out and "app.py:3" in out and "INFO started" not in out

@pytest.mark.skipif(not shutil.which("tesseract"), reason="tesseract not installed")
def test_screenshot_ocr(tmp_path):
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGB", (900, 160), "white"); d = ImageDraw.Draw(im)
    try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    except Exception: font = None
    d.text((20, 20), "Windows protected your PC", fill="black", font=font)
    d.text((20, 80), "Microsoft Defender SmartScreen prevented an unrecognized app", fill="black", font=font)
    p = tmp_path / "s.png"; im.save(p)
    assert "SmartScreen" in engine.render(cli.ocr_image(str(p)))

def test_gui_requires_token_and_explains():
    import http.client, json, re, io, contextlib
    from explainthis import gui
    buf = io.StringIO()
    def run():
        with contextlib.redirect_stdout(buf): gui.serve(open_browser=False)
    threading.Thread(target=run, daemon=True).start()
    for _ in range(100):
        if "?t=" in buf.getvalue(): break
        time.sleep(0.1)
    url = re.search(r"http://127.0.0.1:(\d+)/\?t=(\S+)", buf.getvalue()); port, tok = int(url[1]), url[2]
    c = http.client.HTTPConnection("127.0.0.1", port); c.request("GET", "/"); assert c.getresponse().status == 403
    c = http.client.HTTPConnection("127.0.0.1", port); c.request("POST", f"/explain?t={tok}", json.dumps({"text": "ZeroDivisionError: division by zero"}))
    assert "Division by zero" in json.loads(c.getresponse().read())["text"]

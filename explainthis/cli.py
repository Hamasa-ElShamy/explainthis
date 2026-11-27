import argparse, os, re, shutil, subprocess, sys, tempfile, time
from . import engine

ERR_HINT = re.compile(r"(error|exception|traceback|failed|fatal|denied|not found|refused|timed out|ERR_|cannot|can't|unable)", re.I)


def ocr_image(path):
    if not os.path.isfile(path): sys.exit(f"explainthis: file not found: {path}")
    if not shutil.which("tesseract"):
        sys.exit("OCR needs the free `tesseract` program (sudo apt install tesseract-ocr, brew install tesseract, or the Windows installer).")
    langs = "eng+ara" if "ara" in subprocess.run(["tesseract", "--list-langs"], capture_output=True, text=True).stdout else "eng"
    r = subprocess.run(["tesseract", path, "-", "-l", langs, "--psm", "6"], capture_output=True, text=True)
    return r.stdout


def screen_region(region=None):
    """Capture the screen (needs Pillow's ImageGrab on Windows/macOS, or `grim`/`scrot`/`import` on Linux)."""
    f = tempfile.mktemp(suffix=".png")
    try:
        from PIL import ImageGrab
        im = ImageGrab.grab()
        if region: im = im.crop(region)
        im.save(f); return f
    except Exception:
        pass
    for cmd in (["grim", f], ["scrot", f], ["import", "-window", "root", f]):
        if shutil.which(cmd[0]):
            if subprocess.run(cmd, capture_output=True).returncode == 0 and os.path.exists(f): return f
    sys.exit("Could not capture the screen. Install Pillow (pip install pillow) or scrot/grim, or save a screenshot and use --image FILE.")


def clipboard():
    for cmd in (["wl-paste"], ["xclip", "-selection", "clipboard", "-o"], ["xsel", "-b"], ["pbpaste"], ["powershell", "-command", "Get-Clipboard"]):
        if shutil.which(cmd[0]):
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode == 0: return r.stdout
    sys.exit("No clipboard tool found (wl-paste, xclip, xsel, pbpaste or PowerShell).")


def run_cmd(cmd, lang):
    """Run a command, pass its output through, and explain automatically if it failed."""
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
    except OSError as e:
        why = "command not found" if (isinstance(e, FileNotFoundError) or not shutil.which(cmd[0])) else (e.strerror or str(e))
        print(f"explainthis: cannot run '{cmd[0]}': {why}. Check the spelling, and that the program is installed and on your PATH." if lang == "en" else f"explainthis: مش قادر أشغل '{cmd[0]}': {why}. راجع الإملاء واتأكد إن البرنامج متسطب.", file=sys.stderr)
        return 127
    buf = []
    for line in p.stdout:
        sys.stdout.write(line); buf.append(line)
    code = p.wait()
    if code != 0:
        print(f"\n--- ExplainThis: the command exited with code {code} ---" if lang == "en" else f"\n--- ExplainThis: الأمر انتهى بكود {code} ---")
        print(engine.render("".join(buf[-300:]), lang))
    return code


def watch(path, lang, poll=1.0, once=False):
    """Follow a log file; explain each new error block automatically."""
    with open(path, errors="replace") as f:
        if not once: f.seek(0, 2)
        block, last, done = [], time.time(), set()
        while True:
            line = f.readline()
            if line:
                if block and not (line.startswith((" ", "\t")) or ERR_HINT.search(line)):
                    flush(block, lang, done); block = []
                if ERR_HINT.search(line) or block: block.append(line)
                last = time.time(); continue
            if block and time.time() - last > poll / 2:
                flush(block, lang, done); block = []
            if once and not block: return
            time.sleep(poll / 4)


def flush(block, lang, done):
    txt = "".join(block)
    k = engine.key_line(txt)
    if k in done: return
    done.add(k)
    r = engine.explain(txt, lang)
    if r["matches"]:
        print("=" * 60); print(engine.render(txt, lang), flush=True)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="explainthis", description="Explain an error or warning. Reads it automatically from a command, a log, the clipboard, a pipe or a screenshot.")
    ap.add_argument("--lang", choices=["en", "ar"], default="en")
    s = ap.add_subparsers(dest="cmd")
    r = s.add_parser("run", help="run a command and explain it automatically if it fails"); r.add_argument("command", nargs=argparse.REMAINDER)
    w = s.add_parser("watch", help="follow a log file and explain new errors"); w.add_argument("file"); w.add_argument("--from-start", action="store_true")
    s.add_parser("clipboard", help="explain whatever text is on the clipboard")
    i = s.add_parser("image", help="OCR a screenshot file and explain it"); i.add_argument("file")
    sc = s.add_parser("screen", help="capture the screen, OCR it and explain"); sc.add_argument("--region", help="x1,y1,x2,y2")
    t = s.add_parser("text", help="explain text given as arguments"); t.add_argument("words", nargs="*")
    g = s.add_parser("gui", help="open the local window"); g.add_argument("--no-open", action="store_true")
    o = ap.parse_args(argv)
    if o.cmd == "run":
        cmd = o.command[1:] if o.command and o.command[0] == "--" else o.command
        if not cmd: sys.exit("usage: explainthis run -- COMMAND ARGS")
        sys.exit(run_cmd(cmd, o.lang))
    if o.cmd == "watch": return watch(o.file, o.lang, once=o.from_start)
    if o.cmd == "clipboard": print(engine.render(clipboard(), o.lang)); return
    if o.cmd == "image": print(engine.render(ocr_image(o.file), o.lang)); return
    if o.cmd == "screen":
        reg = tuple(int(x) for x in o.region.split(",")) if o.region else None
        print(engine.render(ocr_image(screen_region(reg)), o.lang)); return
    if o.cmd == "text":
        txt = " ".join(o.words) if o.words else ("" if sys.stdin.isatty() else sys.stdin.read())
        if not txt.strip(): sys.exit("explainthis: no text given. Pass the message as arguments or pipe it in: some-command 2>&1 | explainthis text")
        print(engine.render(txt, o.lang)); return
    if o.cmd == "gui":
        from . import gui; return gui.serve(open_browser=not o.no_open)
    if not sys.stdin.isatty():
        print(engine.render(sys.stdin.read(), o.lang)); return
    ap.print_help()


if __name__ == "__main__":
    main()

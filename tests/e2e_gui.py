"""Real-browser check of the window. Usage: python tests/e2e_gui.py /usr/bin/google-chrome"""
import re, subprocess, sys, time
from playwright.sync_api import sync_playwright
chrome = sys.argv[1] if len(sys.argv) > 1 else "/usr/bin/google-chrome"
p = subprocess.Popen([sys.executable, "-m", "explainthis.cli", "gui", "--no-open"], stdout=subprocess.PIPE, text=True)
url = re.search(r"http://\S+", p.stdout.readline())[0]
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=chrome, args=["--no-sandbox"]); g = b.new_page(viewport={"width": 900, "height": 760})
    g.goto(url)
    g.fill("#t", "Traceback (most recent call last):\n  File \"app.py\", line 7, in <module>\n    import yaml\nModuleNotFoundError: No module named 'yaml'")
    g.click("button"); g.wait_for_function("document.getElementById('o').textContent.includes('pyyaml')", timeout=8000)
    g.screenshot(path="demo/gui-explain.png"); print("e2e ok:", g.inner_text("#o")[:60].replace("\n", " | "))
    b.close()
p.terminate()

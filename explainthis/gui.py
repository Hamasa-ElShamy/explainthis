"""Small local window: paste an error or choose a screenshot. Served on 127.0.0.1 only, with a random token."""
import base64, http.server, json, os, secrets, tempfile, threading, webbrowser
from . import engine, cli

PAGE = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>ExplainThis</title>
<style>body{font:16px system-ui;max-width:760px;margin:30px auto;padding:0 16px;background:#0f1419;color:#e6edf3}textarea{width:100%;height:150px;background:#161c24;color:#e6edf3;border:1px solid #30363d;border-radius:8px;padding:10px;font:14px monospace}
button,label.b{font:inherit;font-weight:700;background:#f0883e;color:#1a1005;border:0;border-radius:8px;padding:10px 16px;font-weight:700;cursor:pointer;margin:6px 6px 6px 0;display:inline-block}pre{white-space:pre-wrap;background:#161c24;border:1px solid #30363d;border-radius:8px;padding:14px}select{padding:8px;border-radius:8px}</style>
<h1>ExplainThis</h1><p>Paste an error or warning, or choose a screenshot. Nothing is sent anywhere and nothing is run for you.</p>
<textarea id=t placeholder="Paste the error text here"></textarea><br>
<button onclick=go()>Explain</button><label class=b>Screenshot...<input id=f type=file accept="image/*" hidden onchange=img()></label>
<select id=l><option value=en>English</option><option value=ar>العربية</option></select><pre id=o></pre>
<script>const T="__TOKEN__";
async function post(b){const r=await fetch("/explain?t="+T,{method:"POST",body:JSON.stringify(b)});return (await r.json()).text}
async function go(){o.textContent=await post({text:t.value,lang:l.value})}
function img(){const r=new FileReader();r.onload=async()=>{o.textContent="Reading the image...";o.textContent=await post({image:r.result.split(",")[1],lang:l.value})};r.readAsDataURL(f.files[0])}</script>"""


def serve(open_browser=True, port=0):
    token = secrets.token_urlsafe(16)

    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a): pass
        def _ok(self, body, ctype="text/html; charset=utf-8"):
            self.send_response(200); self.send_header("Content-Type", ctype); self.end_headers(); self.wfile.write(body)
        def do_GET(self):
            if self.path.split("?t=")[-1] != token: self.send_response(403); self.end_headers(); return
            self._ok(PAGE.replace("__TOKEN__", token).encode())
        def do_POST(self):
            if "t=" + token not in self.path: self.send_response(403); self.end_headers(); return
            d = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            try:
                text = d.get("text", "")
                if d.get("image"):
                    f = tempfile.mktemp(suffix=".png"); open(f, "wb").write(base64.b64decode(d["image"]))
                    text = cli.ocr_image(f); os.remove(f)
                out = engine.render(text, d.get("lang", "en"))
            except SystemExit as e:
                out = str(e)
            self._ok(json.dumps({"text": out}).encode(), "application/json")

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), H)
    url = f"http://127.0.0.1:{srv.server_port}/?t={token}"
    print("ExplainThis window:", url, flush=True)
    if open_browser: threading.Thread(target=lambda: webbrowser.open(url), daemon=True).start()
    try: srv.serve_forever()
    except KeyboardInterrupt: pass

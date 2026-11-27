import re, sys, os
from .kb import E, PKG, HTTP_MEANING

RISK_AR = {"High": "عالي", "Medium": "متوسط", "Low": "منخفض"}
_FRAME = re.compile(r'File "(?P<file>[^"]+)", line (?P<line>\d+)(?:, in (?P<func>\S+))?')
_NODE = re.compile(r"at (?:(?P<func>[^\s(]+) )?\(?(?P<file>[^\s():]+):(?P<line>\d+):(?P<col>\d+)\)?")


def locate(text):
    """Where it happened: the last Python frame (+ its code line) or the first Node frame outside node_modules."""
    lines = text.splitlines()
    last = None
    for i, l in enumerate(lines):
        m = _FRAME.search(l)
        if m:
            code = lines[i + 1].strip() if i + 1 < len(lines) and not lines[i + 1].lstrip().startswith(("File ", "Traceback")) else ""
            last = dict(file=m["file"], line=m["line"], func=m["func"] or "", code=code)
    if last:
        return last
    for l in lines:
        m = _NODE.search(l)
        if m and "node_modules" not in l and "node:internal" not in l:
            return dict(file=m["file"], line=m["line"], func=m["func"] or "", code="")
    return None


def key_line(text):
    """The line that most likely names the error (last line that looks like Name: message, else last non-empty)."""
    cand = [l.strip() for l in text.splitlines() if l.strip()]
    for l in reversed(cand):
        if re.match(r"^[A-Za-z_.]*(Error|Exception|Warning|Exit)\b.*:|^(fatal|error|ERR|npm ERR!|npm error)\b", l):
            return l
    return cand[-1] if cand else ""


def _fill(s, d):
    class D(dict):
        def __missing__(self, k): return "{" + k + "}"
    return s.format_map(D(d))


def explain(text, lang="en"):
    """-> dict with matches (best first) or an honest 'unknown'. Never runs anything."""
    i = 0 if lang == "en" else 1
    out = dict(where=locate(text), key=key_line(text), matches=[])
    seen = set()
    for e in E:
        for rx in e["rx"]:
            m = re.search(rx, text, re.M | re.I)
            if not m or e["id"] in seen:
                continue
            seen.add(e["id"])
            g = {k: (v if v is not None else "") for k, v in m.groupdict().items()}
            g["py"] = "python3" if os.name != "nt" else "py"
            if "mod" in g and g["mod"]:
                top = g["mod"].split(".")[0]
                g["mod"] = top
                g["pkg"] = PKG.get(top, top)
                g["pkgnote"] = f" (here: `{top}` is installed as `{PKG[top]}`)" if top in PKG else ""
                g["pkgnote_ar"] = f" (هنا `{top}` بتتسطب باسم `{PKG[top]}`)" if top in PKG else ""
            if "k" in g: g["k"] = g["k"].strip()
            if e["id"] == "http-status":
                mm = HTTP_MEANING.get(g.get("code", ""), ("", ""))
                g["codemean_en"], g["codemean_ar"] = mm
            if e["id"] == "win-dll" and not g.get("dll"): g["dll"] = g.get("dll2", "")
            if e["id"] == "git-conflict" and not g.get("f"): g["f"] = "the conflicted file"
            out["matches"].append(dict(
                id=e["id"], risk=e["risk"], title=_fill(e["title"][i], g), meaning=_fill(e["mean"][i], g),
                steps=[_fill(s, g) for s in e["steps"][i]],
                consequence=_fill(e["consequence"][i], g) if e["consequence"] else None))
            break
    return out


def render(text, lang="en"):
    r = explain(text, lang)
    ar = lang == "ar"
    L = []
    if not r["matches"]:
        L.append("مش عارف الرسالة دي." if ar else "I do not have a built-in explanation for this message.")
        L.append(("السطر الأهم: " if ar else "Key line: ") + r["key"][:300])
        if r["where"]:
            w = r["where"]; L.append(("حصلت في: " if ar else "Where: ") + f"{w['file']}:{w['line']} {w['func']}".strip())
            if w["code"]: L.append(("الكود: " if ar else "Code: ") + w["code"])
        q = re.sub(r"[\w./\\-]*[/\\][\w./\\-]*", "", r["key"])[:120].strip()
        L.append(("ممكن تدور على: " if ar else "Try searching for the message text without your own file names: ") + f'"{q}"')
        L.append("(الأداة بتشرح الرسائل المعروفة بس ومش بتخمن.)" if ar else "(ExplainThis only explains messages it knows. It does not guess.)")
        return "\n".join(L)
    m = r["matches"][0]
    L.append(("الرسالة: " if ar else "What it says: ") + m["title"])
    if r["where"]:
        w = r["where"]; L.append(("حصلت في: " if ar else "Where: ") + f"{w['file']}:{w['line']}" + (f" ({w['func']})" if w["func"] else ""))
        if w["code"]: L.append(("الكود: " if ar else "Code: ") + w["code"])
    L.append(("المعنى: " if ar else "Meaning: ") + m["meaning"])
    L.append("ممكن تعمل إيه:" if ar else "What you can do:")
    L += [f"  {n}. {s}" for n, s in enumerate(m["steps"], 1)]
    if m["consequence"]:
        L.append(("لو عملت الحل السريع الخطر: " if ar else "If you take the tempting shortcut: ") + m["consequence"])
    if m["risk"]:
        L.append(("درجة الخطورة: " if ar else "Risk: ") + (RISK_AR[m["risk"]] if ar else m["risk"]))
    if len(r["matches"]) > 1:
        L.append(("كمان ظهر: " if ar else "Also found: ") + "; ".join(x["title"] for x in r["matches"][1:]))
    L.append("(الأداة مش بتنفذ أي أمر بدالك.)" if ar else "(ExplainThis never runs a fix or clicks anything for you.)")
    return "\n".join(L)

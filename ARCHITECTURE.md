# ExplainThis: technical notes / الشرح التقني

## English
Pipeline: **source of text** (command output, pipe, log, clipboard, OCR of a screenshot, the window) then **locate** then **match** then **render**.
- `cli.py`: the input sources. `run_cmd` starts the command with stderr merged into stdout, passes every line through unchanged, and only if the exit code is not 0 explains the last 300 lines. `watch` tails a file, groups lines into an error block (a line that looks like an error plus the indented lines after it), waits until the block is quiet, explains it once (the key line is remembered so repeats are skipped). `ocr_image` calls `tesseract` (`eng+ara` if the Arabic data exists). `screen_region` uses Pillow `ImageGrab`, or `grim`, `scrot`, `import`. `clipboard` tries `wl-paste`, `xclip`, `xsel`, `pbpaste`, PowerShell.
- `engine.py`: `locate()` finds the last Python frame and its code line, or the first Node frame outside `node_modules`. `key_line()` picks the line that names the error. `explain()` runs each knowledge entry's regular expressions (case-insensitive) over the text, fills the named groups into the templates (for example the module name and its pip name), and returns every match, best first. `render()` prints one language; when nothing matches it says so and shows the key line, the location and a search hint.
- `kb.py`: the knowledge base: for each entry an id, regexes, English and Arabic title, meaning and steps, an optional consequence of the dangerous shortcut, and a risk level. Tests force every entry to have both languages and a sample.
- `gui.py`: a tiny HTTP server on 127.0.0.1 with a random token in the URL; no token, no access. It calls the same engine.

**Design decisions**: no model, so every sentence traces to a hand-written entry; unknown means unknown; the tool only ever prints. It never executes a suggested step, never presses a button and never changes security settings.

**Limits**: 25 message kinds; OCR text matching only; clipboard and screen capture untested here; Windows entries not run on Windows.

## بالعربي
المسار: مصدر النص (ناتج أمر، pipe، لوج، clipboard، OCR لصورة، النافذة) ثم تحديد المكان ثم مطابقة قاعدة المعرفة ثم العرض. `cli.py` فيه مصادر النص، `engine.py` فيه المطابقة وتحديد الملف والسطر، `kb.py` قاعدة المعرفة بالعربي والإنجليزي، `gui.py` نافذة محلية على 127.0.0.1 بـ token عشوائي. مفيش نموذج ذكاء اصطناعي: كل جملة ليها مدخل مكتوب يدوي. الأداة مش بتنفذ أي أمر مقترح ومش بتضغط أي زرار. الحدود: 25 رسالة بس، والـ OCR بيطابق كلام بس، و clipboard وscreen مش متجربين هنا.

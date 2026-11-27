# ExplainThis

[![tests](https://github.com/mohamed-elshamy-ai/explainthis/actions/workflows/tests.yml/badge.svg)](https://github.com/mohamed-elshamy-ai/explainthis/actions/workflows/tests.yml) ![tests: 40 passing](https://img.shields.io/badge/tests-40%20passing-brightgreen) ![license: MIT](https://img.shields.io/badge/license-MIT-blue)

Don't just look at an error. Understand it. ExplainThis explains error messages and confusing system warnings in plain language (English or Arabic), says what is risky about the tempting shortcut, and **reads the error for you automatically**: from a command that failed, a log file, a pipe, the clipboard, or a screenshot. It never runs a fix and never clicks "Allow" for you. No cloud, no AI service: it runs on your computer.


## Worked examples

Real output, see [`demo/demo-output.txt`](demo/demo-output.txt). The first one is automatic: you run your command through `explainthis run` and it explains only if the command fails.

```
$ explainthis run -- python3 /tmp/t1.py
ModuleNotFoundError: No module named 'cv2'

--- ExplainThis: the command exited with code 1 ---
What it says: Python cannot find the module 'cv2'
Where: /tmp/t1.py:1 (<module>)
Code: import cv2
Meaning: The module is not installed in the Python that ran your script, or its name is spelled differently.
What you can do:
  1. Install it with the same Python that failed: `python3 -m pip install opencv-python`.
  2. The pip name can differ from the import name (here: `cv2` is installed as `opencv-python`). ...

$ cat win-smartscreen.txt | explainthis       # text of the Windows warning
What it says: Windows SmartScreen blocked an unrecognised app
Meaning: Windows cannot check this program's reputation. That is not proof of a virus ...
If you take the tempting shortcut: 'More info' then 'Run anyway' lets the program start with your user's permissions. ... ExplainThis never clicks it for you.
Risk: High
```

The small window: [`demo/gui-explain.png`](demo/gui-explain.png) (a real Chrome run of `tests/e2e_gui.py`).

**Try it without installing:** [browser demo](https://mohamed-elshamy-ai.github.io/explainthis/demo.html). Paste an error message; it runs the same Python in your browser via Pyodide (about 10 MB the first time, loaded from jsDelivr). Nothing you paste is uploaded. Text only: screenshot, clipboard, `run` and `watch` need the installed tool.

## Install and use

```
git clone https://github.com/mohamed-elshamy-ai/explainthis && cd explainthis
pip install .
explainthis run -- python app.py      # runs it, explains automatically if it fails
python app.py 2>&1 | explainthis      # same idea with a pipe
explainthis watch app.log             # follows a log, explains each new error block
explainthis clipboard                 # explain what you just copied
explainthis image screenshot.png      # OCR a screenshot of a warning, then explain
explainthis screen                    # capture the screen, OCR, explain
explainthis gui                       # small local window (paste text or choose a screenshot)
explainthis --lang ar run -- python app.py     # Arabic output
```

| System | Status |
|---|---|
| Linux | Tested (Python 3.10): `run`, pipe, `watch`, `text`, `image` (with tesseract), the window. |
| Windows / macOS | Should work, not tested by a person. On a macOS CI runner the test of the local window (`explainthis gui`) failed and I did not find why, so treat `gui` on macOS as unverified. The command-line parts passed there. |
| Not tested anywhere yet | `clipboard` and `screen` (this machine has no display or clipboard tool). |
| Android | Not available. |

`image` and `screen` need the free `tesseract` program (`sudo apt install tesseract-ocr`, `brew install tesseract`, or the Windows installer). `screen` also needs Pillow (`pip install pillow`) or `scrot`/`grim`.

## What it knows (28 messages)

Python: missing module, file not found, permission denied, KeyError, IndexError, None errors, TypeError, SyntaxError/IndentationError, division by zero, memory, pip "externally-managed-environment". Shell and network: command not found, connection refused, DNS, bad certificate, HTTP 401/403/404/429/5xx, timeout, port in use, disk full. Git: not a repository, push rejected, merge conflict. npm errors. Windows: SmartScreen, UAC prompt, missing DLL, access denied 0x80070005, turning off the firewall.

Each entry has a plain-language meaning, steps, and, where there is a dangerous shortcut, what would happen if you took it and a risk level.

## Limitations

- **It only explains messages it knows (28 kinds).** Anything else gets "I do not have a built-in explanation", the key line, where it happened, and a search suggestion. It does not guess and there is no AI model. A message that matches the wrong entry is possible: the first match wins, others are listed as "Also found".
- **It does not understand a screenshot.** It reads the text with OCR and matches it. A dialog that has no recognisable words (only icons) or poor OCR gets no explanation. There is no vision model.
- No global shortcut, no click-and-drag region picker, no tray app. `screen` takes the whole screen (or `--region x1,y1,x2,y2`).
- The Windows entries were checked against typed copies of the known messages, not on a Windows machine. Git, pip, disk, memory entries are typed from the known messages; Python, bash, network, npm and HTTP samples were captured from real runs (see `tests/samples`).
- It never runs or clicks anything. `run` only runs the command you gave it.
- The explanations are general. They cannot see your machine, so "check X" is advice, not a diagnosis.

## Related tools

Tools that explain terminal errors already exist, for example [errbuddy](https://github.com/sithija-jayasinghe/errbuddy) and [Errxplain](https://github.com/EliaGambalunga/Errxplain), mostly using an AI model. ExplainThis is rule-based and offline, so it handles only 28 known messages, but it covers Windows system warnings (SmartScreen, UAC), says what the risky shortcut would do, reads logs and screenshots, and answers in Arabic.

## Technical notes

[ARCHITECTURE.md](ARCHITECTURE.md), Arabic and English. 40 pytest tests: every knowledge entry has a sample and must be recognised, location extraction, Arabic output, run on failure and silence on success, log watching, screenshot OCR, the window with its token. Output: [`demo/test-output.txt`](demo/test-output.txt).

## How it works

You run your command through `explainthis run`, which passes the output through unchanged. If the command fails, ExplainThis takes the error text and looks for the location (file, line and error code). It then matches the message against a hand-written knowledge base (28 message types) that holds the meaning, the steps to take, a warning about the risky shortcut, and a risk level. The same happens when the error comes from a pipe, a log file it follows, the clipboard, or an image read with OCR. If a message is unknown, it says so instead of guessing. It never runs a fix for you.

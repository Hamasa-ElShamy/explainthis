# explainthis design system

Read this before changing the site's UI. Do not introduce a new direction; extend this one. English only. Values below come from `docs/index.html` as of this commit.

## Concept

An error with a sticky note beside it: what it means, where it happened, and what the shortcut risks.

Theme: light (converted from dark on the user's instruction to follow the light-pages rule).

## Color tokens

| Token | Value | Role |
|---|---|---|
| `--bg` | `#ecedea` | page background |
| `--fg` | `#1a1d21` | body text |
| `--mut` | `#4d555e` | secondary text (AA on bg) |
| `--card` | `#ffffff` | card and panel surface |
| `--line` | `#d2d5d0` | borders and dividers |
| `--acc` | `#b13a09` | primary action, links, focus ring |
| `--accfg` | `#ffffff` | text on accent |
| `--code` | `#1a1d21` | code block background |
| `--codefg` | `#ffd9b8` | code block text |
| `--warn` | `#b45309` | warning border and limits |

Contrast: every text node on the page is checked against WCAG AA (4.5:1, 3:1 for large text) with a script in the repo owner's QA harness. Keep it passing when you change a color.

## Type

| Token | Stack | Role |
|---|---|---|
| `--arabic` | `'Readex Pro',sans-serif` | Arabic font stack |
| `--body` | `'Manrope','Readex Pro',system-ui,sans-serif` | body font stack |
| `--head` | `'Bricolage Grotesque','Readex Pro',system-ui,sans-serif` | heading font stack |

Font sizes in use: `.86rem`, `1.5rem`, `1rem`, `.9rem`, `.72rem`, `clamp(2.1rem,8.5vw,3.1rem)`, `1.2rem`, `clamp(2.2rem,7vw,4rem)`, `1.15rem`, `.92rem`.

## Spacing, radius, elevation

- Spacing values in use: `2px`, `4px`, `6px`, `8px`, `10px`, `11px`, `12px`, `14px`, `16px`, `18px`, `26px`, `40px`. Prefer these; do not add new ones.
- Radius: `--r` (10px). Use the token, not literals.
- Elevation: `0 14px 22px rgba(0,0,0,.2)!important`, `0 16px 26px -14px rgba(0,0,0,.5)`, `0 18px 30px rgba(0,0,0,.45)`

## Motion

- Durations in use: `.05s`, `.15s`, `.25s`, `.2s`, `.34s`, `.35s`, `.42s`, `.45s`, `.8s`, `.9s`, `1.2s`, `1s`.
- Curves: `cubic-bezier(.16,1,.3,1)`, `cubic-bezier(.22,1.36,.32,1)`.
- Every animation sits behind `prefers-reduced-motion: reduce`, which turns animation and transition off.
- Motion shows state or order. It is never decoration.

## Components and states

- Button `.btn` (filled) and `.btn.alt` (outline): min height 44px, visible `:focus-visible` outline (2px accent), hover and active states.
- Card `.card`, warning card `.card.warn` (left border in `--warn`).
- Language toggle `.langtoggle` with `aria-pressed`.
- Code block `pre`: always LTR, monospace.
- Status words use `.ok b` and `.no b` colors (AA checked).

## RTL rules

- The language toggle sets `dir` and `lang` on `<html>`. Arabic text uses the `--arabic` font and line-height 1.75.
- Use logical CSS (`margin-inline`, `inset-inline-start`, `text-align:start`). No `left` or `right` for layout.
- Letter-spacing is 0 and text-transform none in Arabic.
- Code, terminal output and demo panels stay LTR (`direction:ltr`). Install and demo output stay English.
- Arabic is Egyptian-leaning plain language. Brand names and commands stay Latin.

## Microcopy voice

Plain, specific, honest about limits. Say what it does and what it does not. No hype, no invented numbers.

Examples from the site:

1. Don't just look at the error. Understand it.
2. Python cannot find the module 'cv2'
3. It never runs a fix for you.
4. Only 28 kinds of message are known.
5. No AI service.

## Do / Don't

| Do | Don't |
|---|---|
| Say what it cannot explain | Guess an explanation |
| Show the risk of the shortcut | Offer a fix button |
| Keep the note beside the error | Hide the original error |
| Orange for the note and risk only | Orange for decoration |
| Plain words first, jargon second | Jargon first |

## Known hard-coded values (should become tokens)

These literal colors appear in the CSS outside `:root`: `#0a0e12`, `#17703f`, `#2b1c06`, `#2e9e5b`, `#363d45`, `#3a2227`, `#7e8a96`, `#a8281b`, `#b6c2cf`, `#c0392b`, `#c2410c`, `#e8c98f`, `#ff6b6b`, `#ffb4b4`, `#ffe9bf`.
Also: status colors in `.ok b` and `.no b`, and several literal pixel sizes in component CSS. Move them into tokens next time that block is touched.

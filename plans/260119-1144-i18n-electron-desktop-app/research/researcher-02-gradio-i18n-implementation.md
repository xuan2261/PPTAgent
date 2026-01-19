# Research Report: Gradio i18n Implementation for English/Vietnamese

**Date:** 2026-01-19
**Context:** PPTAgent - Gradio-based presentation generation system (`webui.py`)

---

## 1. Gradio Native i18n Capabilities

### Built-in Features
- Auto-translates standard UI elements (Submit, Clear, etc.) into 40+ languages
- Uses browser locale detection (BCP 47 format: `en`, `vi`, `es-MX`)
- `gr.I18n` class for custom translations

### Supported Component Properties
- `label`, `placeholder`, `title`, `description`, `info`, `value`

### Limitations
- i18n broken in Gradio v6.0-v6.1 (works in v5.x) - reported Dec 2025
- No built-in pluralization handling
- No RTL language support out-of-box
- Dynamic switching requires page reload or state management

---

## 2. Implementation Approaches

### Option A: Native `gr.I18n` (Recommended)

```python
import gradio as gr
import json

# Load translations
with open('locales/en.json', 'r', encoding='utf-8') as f:
    en = json.load(f)
with open('locales/vi.json', 'r', encoding='utf-8') as f:
    vi = json.load(f)

i18n = gr.I18n(en=en, vi=vi)

with gr.Blocks() as demo:
    gr.Markdown(i18n("welcome_message"))
    btn = gr.Button(i18n("generate_button"))

demo.launch(i18n=i18n)
```

**Pros:** Native, no dependencies, browser locale auto-detect
**Cons:** Less flexible dynamic switching

### Option B: `gradio-i18n` Library

```python
from gradio_i18n import Translate, gettext as _
import gradio as gr

translations = {
    "en": {"Hello": "Hello", "Generate": "Generate"},
    "vi": {"Hello": "Xin chao", "Generate": "Tao"}
}

with gr.Blocks() as demo:
    with Translate(translations) as lang:
        gr.Markdown(_("Hello"))
        gr.Button(_("Generate"))

demo.launch()
```

**Pros:** `gettext`-like syntax, `dump_blocks()` for string extraction
**Cons:** External dependency, compatibility concerns with Gradio v6+

---

## 3. JSON Translation File Structure

### Recommended: Separate Files Per Language

```
locales/
├── en.json
└── vi.json
```

### en.json
```json
{
  "app_title": "PPTAgent - AI Presentation Generator",
  "welcome_message": "Welcome to PPTAgent",
  "generate_button": "Generate Presentation",
  "upload_label": "Upload Document",
  "template_select": "Select Template",
  "error_no_file": "Please upload a file first"
}
```

### vi.json
```json
{
  "app_title": "PPTAgent - Tao Trinh Bay Bang AI",
  "welcome_message": "Chao mung den voi PPTAgent",
  "generate_button": "Tao Trinh Bay",
  "upload_label": "Tai Len Tai Lieu",
  "template_select": "Chon Mau",
  "error_no_file": "Vui long tai len tep truoc"
}
```

---

## 4. Dynamic Language Switching

### Approach 1: Dropdown + State (Recommended)

```python
import gradio as gr
import json

def load_translations():
    translations = {}
    for lang in ['en', 'vi']:
        with open(f'locales/{lang}.json', 'r', encoding='utf-8') as f:
            translations[lang] = json.load(f)
    return translations

TRANSLATIONS = load_translations()

def get_text(key, lang='en'):
    return TRANSLATIONS.get(lang, {}).get(key, key)

with gr.Blocks() as demo:
    lang_state = gr.State('en')
    lang_dropdown = gr.Dropdown(
        choices=[('English', 'en'), ('Tieng Viet', 'vi')],
        value='en',
        label="Language"
    )

    title = gr.Markdown(get_text("welcome_message", "en"))
    btn = gr.Button(get_text("generate_button", "en"))

    def update_ui(lang):
        return (
            get_text("welcome_message", lang),
            get_text("generate_button", lang),
            lang
        )

    lang_dropdown.change(
        update_ui,
        inputs=[lang_dropdown],
        outputs=[title, btn, lang_state]
    )
```

### Approach 2: URL Parameter

```python
# Read from query param: ?lang=vi
request = gr.Request()
lang = request.query_params.get("lang", "en")
```

---

## 5. Best Practices

| Practice | Description |
|----------|-------------|
| UTF-8 encoding | Always use `encoding='utf-8'` for JSON files |
| Descriptive keys | Use `upload_document_label` not `label1` |
| Fallback chain | `vi` -> `en` -> key itself |
| Isolate strings | All UI text in translation files, none hardcoded |
| Key consistency | Same keys across all language files |
| Context comments | Add `_comment` fields for translators |

### File Organization for PPTAgent

```
PPTAgent/
├── locales/
│   ├── en.json          # English (default)
│   ├── vi.json          # Vietnamese
│   └── README.md        # Translation guidelines
├── webui.py             # Import i18n helper
└── utils/
    └── i18n.py          # Translation helper module
```

---

## 6. Recommendation for PPTAgent

**Use Native `gr.I18n` with JSON files:**
1. Gradio v5.x compatibility (verify current version)
2. No external dependencies
3. Browser locale auto-detection
4. Add manual dropdown for explicit switching

**Implementation Steps:**
1. Create `locales/` directory with `en.json`, `vi.json`
2. Create `utils/i18n.py` helper module
3. Modify `webui.py` to use `gr.I18n`
4. Add language dropdown component
5. Test with browser locale changes

---

## Sources

- [Gradio i18n Documentation](https://gradio.app)
- [gradio-i18n PyPI](https://pypi.org/project/gradio-i18n/)
- [gradio-i18n GitHub](https://github.com/hanxiao/gradio-i18n)
- [Python gettext Documentation](https://docs.python.org/3/library/gettext.html)

---

## Unresolved Questions

1. Which Gradio version does PPTAgent use? (v5 vs v6 affects i18n approach)
2. Should language preference persist in localStorage/cookies?
3. Do backend agent responses need translation or just UI?

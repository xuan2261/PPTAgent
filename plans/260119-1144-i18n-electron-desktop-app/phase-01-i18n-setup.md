# Phase 1: i18n Infrastructure Setup

## Context Links
- [Plan Overview](plan.md)
- [i18n Research](research/researcher-02-gradio-i18n-implementation.md)
- [webui.py](../../webui.py)

## Overview
- **Priority**: P1
- **Status**: pending
- **Effort**: 2h
- **Description**: Create translation file structure and i18n helper module

## Key Insights
- Gradio native `gr.I18n` preferred over `gradio-i18n` library
- JSON files with UTF-8 encoding required
- Current UI has Chinese labels: "幻灯片页数", "输出类型", "选择模板", "发送", "下载文件"
- Fallback chain: vi → en → key itself

## Requirements

### Functional
- EN/VI translation files with all UI strings
- Helper module for loading/accessing translations
- Fallback to English for missing keys

### Non-Functional
- UTF-8 encoding for Vietnamese diacritics
- Descriptive translation keys
- Easy to add new languages

## Architecture

```
PPTAgent/
├── locales/
│   ├── en.json          # English translations
│   ├── vi.json          # Vietnamese translations
│   └── README.md        # Translation guidelines
└── utils/
    └── i18n.py          # Translation helper
```

## Related Code Files

### Create
- `D:/NCKH_2025/PPTAgent/locales/en.json`
- `D:/NCKH_2025/PPTAgent/locales/vi.json`
- `D:/NCKH_2025/PPTAgent/locales/README.md`
- `D:/NCKH_2025/PPTAgent/utils/i18n.py`

### Modify
- None in this phase

## Implementation Steps

### Step 1: Create locales directory
```bash
mkdir -p locales
```

### Step 2: Create en.json
```json
{
  "_comment": "English translations for PPTAgent WebUI",
  "app_title": "DeepPresenter",
  "pages_label": "Number of slides",
  "pages_auto": "auto",
  "output_type_label": "Output type",
  "output_freeform": "Freeform",
  "output_template": "Template",
  "template_label": "Select template",
  "send_button": "Send",
  "download_button": "Download file",
  "input_placeholder": "Your instruction here",
  "default_instruction": "Please create a PPT based on the uploaded attachments",
  "slide_complete": "Slides generated successfully, click button below to download"
}
```

### Step 3: Create vi.json
```json
{
  "_comment": "Vietnamese translations for PPTAgent WebUI",
  "app_title": "DeepPresenter",
  "pages_label": "Số trang slide",
  "pages_auto": "tự động",
  "output_type_label": "Loại đầu ra",
  "output_freeform": "Tự do",
  "output_template": "Mẫu",
  "template_label": "Chọn mẫu",
  "send_button": "Gửi",
  "download_button": "Tải xuống",
  "input_placeholder": "Nhập hướng dẫn của bạn",
  "default_instruction": "Vui lòng tạo PPT dựa trên tệp đính kèm",
  "slide_complete": "Đã tạo slide thành công, nhấn nút bên dưới để tải"
}
```

### Step 4: Create i18n.py helper
```python
import json
from pathlib import Path
from typing import Optional

LOCALES_DIR = Path(__file__).parent.parent / "locales"
_translations: dict[str, dict[str, str]] = {}

def load_translations() -> dict[str, dict[str, str]]:
    global _translations
    if _translations:
        return _translations
    for lang_file in LOCALES_DIR.glob("*.json"):
        lang = lang_file.stem
        with open(lang_file, "r", encoding="utf-8") as f:
            _translations[lang] = json.load(f)
    return _translations

def get_text(key: str, lang: str = "en") -> str:
    translations = load_translations()
    # Fallback chain: lang -> en -> key
    if lang in translations and key in translations[lang]:
        return translations[lang][key]
    if "en" in translations and key in translations["en"]:
        return translations["en"][key]
    return key

def get_available_languages() -> list[tuple[str, str]]:
    return [("English", "en"), ("Tiếng Việt", "vi")]
```

### Step 5: Create locales/README.md
```markdown
# Translation Guidelines

## Adding New Language
1. Copy `en.json` to `{lang_code}.json`
2. Translate all values (keep keys unchanged)
3. Update `get_available_languages()` in `utils/i18n.py`

## Key Naming
- Use snake_case
- Be descriptive: `pages_label` not `label1`
- Group related keys with common prefix
```

## Todo List
- [ ] Create `locales/` directory
- [ ] Create `locales/en.json` with all UI strings
- [ ] Create `locales/vi.json` with Vietnamese translations
- [ ] Create `locales/README.md` with guidelines
- [ ] Create `utils/i18n.py` helper module
- [ ] Test loading translations

## Success Criteria
- All translation files load without errors
- `get_text()` returns correct translation for each language
- Fallback works when key missing in VI

## Risk Assessment
| Risk | Impact | Mitigation |
|------|--------|------------|
| Missing translations | Low | Fallback to English |
| Encoding issues | Medium | Enforce UTF-8 everywhere |

## Security Considerations
- No user input in translation keys
- Sanitize any dynamic content in translations

## Next Steps
→ Phase 2: Integrate i18n into webui.py

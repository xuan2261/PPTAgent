# Phase 2: WebUI i18n Integration

## Context Links
- [Plan Overview](plan.md)
- [Phase 1: i18n Setup](phase-01-i18n-setup.md)
- [webui.py](../../webui.py)
- [i18n Research](research/researcher-02-gradio-i18n-implementation.md)

## Overview
- **Priority**: P1
- **Status**: pending
- **Effort**: 2h
- **Description**: Integrate i18n into webui.py with language dropdown

## Key Insights
- Current hardcoded Chinese strings in webui.py (lines 117-158)
- Use Gradio State for language tracking
- Dynamic UI update via dropdown.change() callback
- All labels need translation: dropdowns, buttons, placeholders

## Requirements

### Functional
- Language dropdown (EN/VI) in UI
- All UI text uses translation system
- Dynamic switching without page reload
- Default to English

### Non-Functional
- Minimal performance impact
- Clean separation of concerns

## Architecture

```
User selects language
        ↓
Dropdown.change() fires
        ↓
update_ui_language() called
        ↓
All components updated with new translations
        ↓
State stores current language
```

## Related Code Files

### Modify
- `D:/NCKH_2025/PPTAgent/webui.py`

### Reference
- `D:/NCKH_2025/PPTAgent/utils/i18n.py`
- `D:/NCKH_2025/PPTAgent/locales/en.json`

## Implementation Steps

### Step 1: Add imports to webui.py
```python
# Add after line 14
from utils.i18n import get_text, get_available_languages
```

### Step 2: Update CONVERT_MAPPING to use i18n keys
```python
# Replace lines 30-33
def get_convert_mapping(lang: str) -> dict:
    return {
        get_text("output_freeform", lang): ConvertType.DEEPPRESENTER,
        get_text("output_template", lang): ConvertType.PPTAGENT,
    }
```

### Step 3: Add language dropdown in create_interface()
```python
# After gr.Markdown title (line 99-102)
with gr.Row():
    lang_dropdown = gr.Dropdown(
        choices=get_available_languages(),
        value="en",
        label="Language",
        scale=1,
    )
lang_state = gr.State("en")
```

### Step 4: Replace hardcoded labels
```python
# Line 116-121: pages_dd
pages_dd = gr.Dropdown(
    label=get_text("pages_label", "en"),
    choices=[get_text("pages_auto", "en")] + [str(i) for i in range(1, 31)],
    value=get_text("pages_auto", "en"),
    scale=1,
)

# Line 122-127: convert_type_dd
convert_type_dd = gr.Dropdown(
    label=get_text("output_type_label", "en"),
    choices=list(get_convert_mapping("en").keys()),
    value=list(get_convert_mapping("en").keys())[0],
    scale=1,
)

# Line 129-135: template_dd
template_dd = gr.Dropdown(
    label=get_text("template_label", "en"),
    choices=template_choices + [get_text("pages_auto", "en")],
    value=get_text("pages_auto", "en"),
    scale=2,
    visible=False,
)

# Line 147-151: msg_input
msg_input = gr.Textbox(
    placeholder=get_text("input_placeholder", "en"),
    scale=4,
    container=False,
)

# Line 153: send_btn
send_btn = gr.Button(get_text("send_button", "en"), scale=1, variant="primary")

# Line 154-158: download_btn
download_btn = gr.DownloadButton(
    f"📥 {get_text('download_button', 'en')}",
    scale=1,
    variant="secondary",
)
```

### Step 5: Add language change handler
```python
def update_ui_language(lang):
    return (
        gr.update(label=get_text("pages_label", lang)),
        gr.update(
            label=get_text("output_type_label", lang),
            choices=list(get_convert_mapping(lang).keys()),
            value=list(get_convert_mapping(lang).keys())[0],
        ),
        gr.update(label=get_text("template_label", lang)),
        gr.update(placeholder=get_text("input_placeholder", lang)),
        gr.update(value=get_text("send_button", lang)),
        gr.update(value=f"📥 {get_text('download_button', lang)}"),
        lang,
    )

lang_dropdown.change(
    update_ui_language,
    inputs=[lang_dropdown],
    outputs=[
        pages_dd, convert_type_dd, template_dd,
        msg_input, send_btn, download_btn, lang_state
    ],
)
```

### Step 6: Update send_message to use lang_state
```python
# Add lang_state to inputs and use in default instruction
async def send_message(
    message, history, attachments, convert_type_value,
    template_value, num_pages_value, lang, request: gr.Request
):
    # ...
    default_msg = get_text("default_instruction", lang)
    history.append({"role": "user", "content": message or default_msg})
    # ...
    file_content = get_text("slide_complete", lang)
```

## Todo List
- [ ] Add i18n imports to webui.py
- [ ] Create get_convert_mapping() function
- [ ] Add language dropdown component
- [ ] Replace all hardcoded labels with get_text()
- [ ] Implement update_ui_language() handler
- [ ] Update send_message() to use current language
- [ ] Test EN/VI switching
- [ ] Test all UI elements display correctly

## Success Criteria
- Language dropdown visible and functional
- All UI text changes when language switched
- Default messages use selected language
- No JavaScript errors in console

## Risk Assessment
| Risk | Impact | Mitigation |
|------|--------|------------|
| Gradio v6 i18n bugs | High | Pin to Gradio v5.x |
| Missing translation keys | Low | Fallback to English |
| State sync issues | Medium | Test thoroughly |

## Security Considerations
- Validate language code is in allowed list
- No eval() or dynamic code execution

## Next Steps
→ Phase 3: Electron Project Setup

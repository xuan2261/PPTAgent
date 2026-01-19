# Translation Guidelines

## Adding New Language
1. Copy `en.json` to `{lang_code}.json`
2. Translate all values (keep keys unchanged)
3. Update `get_available_languages()` in `utils/i18n.py`

## Key Naming
- Use snake_case
- Be descriptive: `pages_label` not `label1`
- Group related keys with common prefix

## Supported Languages
- `en` - English
- `vi` - Tiếng Việt

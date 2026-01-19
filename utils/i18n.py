"""
i18n helper module for PPTAgent WebUI.
Provides translation loading and access with fallback chain.
"""
import json
from pathlib import Path

LOCALES_DIR = Path(__file__).parent.parent / "locales"
_translations: dict[str, dict[str, str]] = {}


def load_translations() -> dict[str, dict[str, str]]:
    """Load all translation files from locales directory."""
    global _translations
    if _translations:
        return _translations
    for lang_file in LOCALES_DIR.glob("*.json"):
        lang = lang_file.stem
        with open(lang_file, "r", encoding="utf-8") as f:
            _translations[lang] = json.load(f)
    return _translations


def get_text(key: str, lang: str = "en") -> str:
    """
    Get translated text for a key.
    Fallback chain: lang -> en -> key itself.
    """
    translations = load_translations()
    # Fallback chain: lang -> en -> key
    if lang in translations and key in translations[lang]:
        return translations[lang][key]
    if "en" in translations and key in translations["en"]:
        return translations["en"][key]
    return key


def get_available_languages() -> list[tuple[str, str]]:
    """Return list of (display_name, code) tuples for available languages."""
    return [("English", "en"), ("Tiếng Việt", "vi")]


def get_all_translations(lang: str = "en") -> dict[str, str]:
    """Get all translations for a language."""
    translations = load_translations()
    return translations.get(lang, translations.get("en", {}))

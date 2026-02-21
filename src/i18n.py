"""
Internationalisation (i18n) support for EDMC-PowerPlayProgress.

Usage::

    from i18n import t, setup
    setup()                      # call once at plugin startup
    label = t("Copy")            # simple lookup
    msg = t("powerplay_level_fmt").format(rank=3, next_rank=4)  # with placeholders
"""
from __future__ import annotations

import json
import locale
import os

_translations: dict[str, str] = {}
_fallback: dict[str, str] = {}


def _load_file(path: str) -> dict[str, str]:
    """Load a JSON translation file and return it as a dict."""
    try:
        with open(path, encoding='utf-8') as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}


def _find_translation(lang_code: str) -> dict[str, str]:
    """
    Try to find a translation file for *lang_code*.

    Lookup order:
    1. Exact match          – ``translations/fr_FR.json``
    2. Language-only match  – ``translations/fr.json``
    """
    translations_dir = os.path.join(os.path.dirname(__file__), 'translations')

    # 1. Exact match (e.g. "fr_FR")
    exact = os.path.join(translations_dir, f"{lang_code}.json")
    if os.path.exists(exact):
        return _load_file(exact)

    # 2. Language prefix only (e.g. "fr")
    if '_' in lang_code:
        base = lang_code.split('_')[0]
        base_path = os.path.join(translations_dir, f"{base}.json")
        if os.path.exists(base_path):
            return _load_file(base_path)

    return {}


def _detect_lang() -> str:
    """Return the best-guess language code from the system locale."""
    try:
        lang = locale.getdefaultlocale()[0]  # e.g. "fr_FR" or "en_US"
        if lang:
            return lang
    except Exception:
        pass
    return 'en'


def setup() -> None:
    """
    Initialise the i18n system.

    Must be called once before any call to :func:`t`.  It detects the system
    locale, loads the matching translation file, and always loads English as
    the fallback.
    """
    global _translations, _fallback

    translations_dir = os.path.join(os.path.dirname(__file__), 'translations')
    _fallback = _load_file(os.path.join(translations_dir, 'en.json'))

    lang_code = _detect_lang()
    if not lang_code.startswith('en'):
        _translations = _find_translation(lang_code)
    else:
        _translations = {}


def t(key: str) -> str:
    """
    Return the translated string for *key*.

    Lookup order:
    1. Current locale translation
    2. English fallback
    3. The key itself (so the UI never shows an empty string)
    """
    if key in _translations:
        return _translations[key]
    if key in _fallback:
        return _fallback[key]
    return key

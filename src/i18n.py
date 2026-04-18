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
from consts import PLUGIN_NAME
from config import appname # type: ignore # noqa: N813
from EDMCLogging import get_plugin_logger # type: ignore # noqa: N813

_translations: dict[str, str] = {}
_logger = get_plugin_logger(f"{appname}.{PLUGIN_NAME}")
_fallback: dict[str, str] = {}

# Exact mapping of Windows locale names to ISO 639 language codes.
# Used before the generic prefix map so special cases take priority.
_WINDOWS_LOCALE_MAP = {
    'Irish_Ireland': 'ga',
}

# Maps the lowercase language prefix of a Windows locale name (e.g. "french"
# from "French_France") to the corresponding ISO 639-1 code.
_WINDOWS_LANG_PREFIX_MAP = {
    'chinese': 'zh',
    'english': 'en',
    'french': 'fr',
    'german': 'de',
    'irish': 'ga',
    'japanese': 'ja',
    'portuguese': 'pt',
    'russian': 'ru',
    'spanish': 'es',
}


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


def _lang_from_env() -> str | None:
    """
    Return a language code from standard POSIX locale environment variables,
    or *None* if none are set to a useful value.

    Checked in priority order: ``LANGUAGE`` (colon-separated list, first
    entry used), ``LC_ALL``, ``LC_MESSAGES``, ``LANG``.
    Encoding suffixes (``.UTF-8``) and modifier tags (``@euro``) are stripped.
    The sentinel values ``C`` and ``POSIX`` are ignored.
    """
    _SENTINELS = {'', 'c', 'posix'}
    candidates: list[str] = []

    language_var = os.environ.get('LANGUAGE', '')
    if language_var:
        # LANGUAGE is a colon-separated list; take the first non-empty entry.
        candidates.extend(language_var.split(':'))
    for var in ('LC_ALL', 'LC_MESSAGES', 'LANG'):
        val = os.environ.get(var, '')
        if val:
            candidates.append(val)

    for raw in candidates:
        # Strip encoding suffix and locale modifier (e.g. "fr_FR.UTF-8@euro")
        code = raw.split('.')[0].split('@')[0]
        if code.lower() not in _SENTINELS:
            return code.lower()
    return None


def _detect_lang() -> str:
    """
    Return the best-guess ISO 639 language code for the running system.

    Detection order:
    1. POSIX locale environment variables (``LANGUAGE``, ``LC_ALL``,
       ``LC_MESSAGES``, ``LANG``) — primary on Linux and macOS.
    2. ``locale.getlocale()`` after ``setlocale(LC_ALL, '')`` — primary on
       Windows where env vars are not set.  Windows locale names such as
       ``French_France`` are mapped to ISO codes via
       :data:`_WINDOWS_LOCALE_MAP` (exact) then
       :data:`_WINDOWS_LANG_PREFIX_MAP` (prefix).
    3. Falls back to ``'en'`` if nothing can be determined.
    """
    # --- Path 1: env vars (Linux / macOS) ---
    env_lang = _lang_from_env()
    if env_lang is not None:
        _logger.debug(f"Detected language from env: {env_lang}")
        return env_lang

    # --- Path 2: locale.getlocale() (Windows) ---
    try:
        locale.setlocale(locale.LC_ALL, '')
        lang = locale.getlocale()[0]  # e.g. "fr_FR", "en_US", "French_France"
        if lang:
            # Exact Windows locale name (e.g. "Irish_Ireland" -> "ga")
            if lang in _WINDOWS_LOCALE_MAP:
                mapped = _WINDOWS_LOCALE_MAP[lang]
                _logger.debug(f"Detected language (Windows exact map): {mapped}")
                return mapped
            # Generic Windows prefix (e.g. "French_France" -> "french" -> "fr")
            prefix = lang.split('_')[0].lower()
            if prefix in _WINDOWS_LANG_PREFIX_MAP:
                mapped = _WINDOWS_LANG_PREFIX_MAP[prefix]
                _logger.debug(f"Detected language (Windows prefix map): {mapped}")
                return mapped
            # POSIX-style code already in the right format (e.g. "fr_FR")
            mapped = lang.lower()
            _logger.debug(f"Detected language: {mapped}")
            return mapped
    except Exception:
        pass

    _logger.debug("No language detected, falling back to English")
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

"""Tests for the src.i18n translation module."""
import sys
import os
import unittest
from unittest.mock import patch

# Ensure the src package is importable without EDMC runtime modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import i18n


class TestI18nSetup(unittest.TestCase):
    """Test that setup() loads translations correctly."""

    def setUp(self):
        # Reset module-level state before each test
        i18n._translations = {}
        i18n._fallback = {}

    def test_setup_loads_english_fallback(self):
        with patch('locale.getdefaultlocale', return_value=('en_US', 'UTF-8')):
            i18n.setup()
        self.assertGreater(len(i18n._fallback), 0)
        self.assertEqual(i18n._fallback.get('Copy'), 'Copy')

    def test_setup_loads_french(self):
        with patch('locale.getdefaultlocale', return_value=('fr_FR', 'UTF-8')):
            i18n.setup()
        self.assertGreater(len(i18n._translations), 0)
        self.assertEqual(i18n._translations.get('Copy'), 'Copier')

    def test_setup_loads_german(self):
        with patch('locale.getdefaultlocale', return_value=('de_DE', 'UTF-8')):
            i18n.setup()
        self.assertEqual(i18n._translations.get('Copy'), 'Kopieren')

    def test_setup_loads_irish(self):
        with patch('locale.getdefaultlocale', return_value=('ga_IE', 'UTF-8')):
            i18n.setup()
        self.assertEqual(i18n._translations.get('Copy'), 'Cóipeáil')

    def test_setup_lang_prefix_fallback(self):
        """A locale like 'fr_CA' should fall back to fr.json."""
        with patch('locale.getdefaultlocale', return_value=('fr_CA', 'UTF-8')):
            i18n.setup()
        self.assertEqual(i18n._translations.get('Reset'), 'Réinitialiser')

    def test_setup_unknown_locale_uses_empty_translations(self):
        with patch('locale.getdefaultlocale', return_value=('xx_XX', 'UTF-8')):
            i18n.setup()
        self.assertEqual(i18n._translations, {})

    def test_english_locale_leaves_translations_empty(self):
        with patch('locale.getdefaultlocale', return_value=('en_GB', 'UTF-8')):
            i18n.setup()
        self.assertEqual(i18n._translations, {})


class TestI18nT(unittest.TestCase):
    """Test the t() lookup function."""

    def setUp(self):
        i18n._translations = {}
        i18n._fallback = {}

    def test_returns_translation_when_available(self):
        i18n._translations = {'Copy': 'Kopieren'}
        i18n._fallback = {'Copy': 'Copy'}
        self.assertEqual(i18n.t('Copy'), 'Kopieren')

    def test_falls_back_to_english(self):
        i18n._translations = {}
        i18n._fallback = {'Copy': 'Copy'}
        self.assertEqual(i18n.t('Copy'), 'Copy')

    def test_falls_back_to_key_when_missing_everywhere(self):
        i18n._translations = {}
        i18n._fallback = {}
        self.assertEqual(i18n.t('nonexistent_key'), 'nonexistent_key')

    def test_format_string_placeholder(self):
        i18n._fallback = {'version_available': 'Version {version} available'}
        result = i18n.t('version_available').format(version='1.2.3')
        self.assertEqual(result, 'Version 1.2.3 available')

    def test_all_english_keys_present(self):
        """Every key in en.json must be returned by t() when fallback is loaded."""
        with patch('locale.getdefaultlocale', return_value=('en_US', 'UTF-8')):
            i18n.setup()
        import json
        en_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'translations', 'en.json')
        with open(en_path, encoding='utf-8') as f:
            en = json.load(f)
        for key, value in en.items():
            with self.subTest(key=key):
                self.assertEqual(i18n.t(key), value)

    def test_irish_all_keys_present(self):
        """Every key in en.json must exist in ga.json."""
        import json
        en_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'translations', 'en.json')
        ga_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'translations', 'ga.json')
        with open(en_path, encoding='utf-8') as f:
            en = json.load(f)
        with open(ga_path, encoding='utf-8') as f:
            ga = json.load(f)
        for key in en:
            with self.subTest(key=key):
                self.assertIn(key, ga)


class TestDetectLang(unittest.TestCase):
    """Test the locale detection helper."""

    def test_returns_locale_code(self):
        with patch('locale.getdefaultlocale', return_value=('fr_FR', 'UTF-8')):
            self.assertEqual(i18n._detect_lang(), 'fr_FR')

    def test_returns_en_on_none(self):
        with patch('locale.getdefaultlocale', return_value=(None, None)):
            self.assertEqual(i18n._detect_lang(), 'en')

    def test_returns_en_on_exception(self):
        with patch('locale.getdefaultlocale', side_effect=ValueError):
            self.assertEqual(i18n._detect_lang(), 'en')


if __name__ == '__main__':
    unittest.main()

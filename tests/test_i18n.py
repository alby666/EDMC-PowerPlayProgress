"""Tests for the src.i18n translation module."""
import locale
import sys
import os
import unittest
from unittest.mock import patch

# Ensure the src package is importable without EDMC runtime modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock EDMC-provided modules that are only available at runtime
from unittest.mock import MagicMock
_mock_config = MagicMock()
_mock_config.appname = 'EDMarketConnector'
sys.modules.setdefault('config', _mock_config)
sys.modules.setdefault('EDMCLogging', MagicMock())

import i18n


class TestI18nSetup(unittest.TestCase):
    """Test that setup() loads translations correctly."""

    def setUp(self):
        # Reset module-level state before each test
        i18n._translations = {}
        i18n._fallback = {}

    def test_setup_loads_english_fallback(self):
        with patch.object(i18n, '_detect_lang', return_value='en_us'):
            i18n.setup()
        self.assertGreater(len(i18n._fallback), 0)
        self.assertEqual(i18n._fallback.get('Copy'), 'Copy')

    def test_setup_loads_french(self):
        with patch.object(i18n, '_detect_lang', return_value='fr_fr'):
            i18n.setup()
        self.assertGreater(len(i18n._translations), 0)
        self.assertEqual(i18n._translations.get('Copy'), 'Copier')

    def test_setup_loads_german(self):
        with patch.object(i18n, '_detect_lang', return_value='de_de'):
            i18n.setup()
        self.assertEqual(i18n._translations.get('Copy'), 'Kopieren')

    def test_setup_loads_irish(self):
        with patch.object(i18n, '_detect_lang', return_value='ga'):
            i18n.setup()
        self.assertEqual(i18n._translations.get('Copy'), 'Cóipeáil')

    def test_setup_lang_prefix_fallback(self):
        """A locale like 'fr_ca' should fall back to fr.json."""
        with patch.object(i18n, '_detect_lang', return_value='fr_ca'):
            i18n.setup()
        self.assertEqual(i18n._translations.get('Reset'), 'Réinitialiser')

    def test_setup_unknown_locale_uses_empty_translations(self):
        with patch.object(i18n, '_detect_lang', return_value='xx_xx'):
            i18n.setup()
        self.assertEqual(i18n._translations, {})

    def test_english_locale_leaves_translations_empty(self):
        with patch.object(i18n, '_detect_lang', return_value='en_gb'):
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
        with patch.object(i18n, '_detect_lang', return_value='en_us'):
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

    # --- Env var path (Linux / macOS) ---

    def test_language_env_var_takes_first_entry(self):
        """LANGUAGE=fr_FR:en should return 'fr_fr'."""
        with patch.dict('os.environ', {'LANGUAGE': 'fr_FR:en'}, clear=True):
            self.assertEqual(i18n._detect_lang(), 'fr_fr')

    def test_lang_env_var_strips_encoding(self):
        """LANG=de_DE.UTF-8 should return 'de_de'."""
        with patch.dict('os.environ', {'LANG': 'de_DE.UTF-8'}, clear=True):
            self.assertEqual(i18n._detect_lang(), 'de_de')

    def test_lang_env_var_strips_modifier(self):
        """LANG=ja_JP.UTF-8@euro should return 'ja_jp'."""
        with patch.dict('os.environ', {'LANG': 'ja_JP.UTF-8@euro'}, clear=True):
            self.assertEqual(i18n._detect_lang(), 'ja_jp')

    def test_c_sentinel_falls_through_to_locale(self):
        """LANG=C should be ignored and fall through to locale.getlocale()."""
        with patch.dict('os.environ', {'LANG': 'C'}, clear=True):
            with patch('locale.setlocale'):
                with patch('locale.getlocale', return_value=('fr_FR', 'UTF-8')):
                    self.assertEqual(i18n._detect_lang(), 'fr_fr')

    def test_lc_messages_used_when_lang_absent(self):
        """LC_MESSAGES should be used when LANGUAGE and LC_ALL are absent."""
        with patch.dict('os.environ', {'LC_MESSAGES': 'ru_RU.UTF-8'}, clear=True):
            self.assertEqual(i18n._detect_lang(), 'ru_ru')

    # --- Windows locale path ---

    def test_returns_posix_locale_code_lowercased(self):
        """POSIX locale name 'fr_FR' from getlocale() should return 'fr_fr'."""
        with patch.dict('os.environ', {}, clear=True):
            with patch('locale.setlocale'):
                with patch('locale.getlocale', return_value=('fr_FR', 'UTF-8')):
                    self.assertEqual(i18n._detect_lang(), 'fr_fr')

    def test_windows_french_france_maps_to_fr(self):
        with patch.dict('os.environ', {}, clear=True):
            with patch('locale.setlocale'):
                with patch('locale.getlocale', return_value=('French_France', 'cp1252')):
                    self.assertEqual(i18n._detect_lang(), 'fr')

    def test_windows_german_germany_maps_to_de(self):
        with patch.dict('os.environ', {}, clear=True):
            with patch('locale.setlocale'):
                with patch('locale.getlocale', return_value=('German_Germany', 'cp1252')):
                    self.assertEqual(i18n._detect_lang(), 'de')

    def test_windows_irish_ireland_exact_map_to_ga(self):
        """Irish_Ireland is in the exact map and should take priority."""
        with patch.dict('os.environ', {}, clear=True):
            with patch('locale.setlocale'):
                with patch('locale.getlocale', return_value=('Irish_Ireland', 'cp1252')):
                    self.assertEqual(i18n._detect_lang(), 'ga')

    def test_returns_en_when_getlocale_returns_none(self):
        """getlocale() returning None (macOS edge case) should fall back to 'en'."""
        with patch.dict('os.environ', {}, clear=True):
            with patch('locale.setlocale'):
                with patch('locale.getlocale', return_value=(None, None)):
                    self.assertEqual(i18n._detect_lang(), 'en')

    def test_returns_en_on_setlocale_exception(self):
        with patch.dict('os.environ', {}, clear=True):
            with patch('locale.setlocale', side_effect=locale.Error):
                self.assertEqual(i18n._detect_lang(), 'en')


if __name__ == '__main__':
    unittest.main()

"""
Sanskrit Abhidhana - Comprehensive Automated Test Suite
Tests transliteration engine, database layer, API endpoints, FTS search, and memory limit compliance.
"""

import unittest
import os
import sys
import site

# Include user site packages in sys.path
user_site = site.getusersitepackages()
if user_site and os.path.exists(user_site) and user_site not in sys.path:
    sys.path.insert(0, user_site)

# Ensure root directory is in sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.transliterate import detect_script, slp1_to_iast, slp1_to_devanagari, slp1_to_ascii, normalize_ascii, to_slp1_key
from app.parser import parse_mw_entry
from app.database import search_by_headword, search_english_fts, autocomplete_headwords
from fastapi.testclient import TestClient
from app.main import app

class TestSanskritAbhidhana(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_01_script_detection(self):
        self.assertEqual(detect_script('कृष्ण'), 'devanagari')
        self.assertEqual(detect_script('kṛṣṇa'), 'iast')
        self.assertEqual(detect_script('krishna'), 'ascii')

    def test_02_transliteration_conversions(self):
        # SLP1 -> IAST
        self.assertEqual(slp1_to_iast('kfzRa'), 'kṛṣṇa')

        # SLP1 -> Devanagari
        self.assertEqual(slp1_to_devanagari('kfzRa'), 'कृष्ण')

        # SLP1 -> ASCII
        self.assertEqual(slp1_to_ascii('kfzRa'), 'krishna')

    def test_03_xml_parser(self):
        sample_xml = '<H1><h><key1>kfzRa</key1><key2>kfzRa/</key2><hom>1</hom></h><body><hom>1.</hom> <s>kfzRa/</s> <lex>mf(<s>A/</s>)n.</lex> black, dark</body><tail><L>55142</L><pc>306,3</pc></tail></H1>'
        parsed = parse_mw_entry('kfzRa', 55142.0, sample_xml, include_raw_xml=True)
        self.assertEqual(parsed['key_slp1'], 'kfzRa')
        self.assertEqual(parsed['headword_iast'], 'kṛṣṇa')
        self.assertEqual(parsed['headword_devanagari'], 'कृष्ण')
        self.assertEqual(parsed['grammatical_code'], 'mf(A/)n.')
        self.assertEqual(parsed['grammatical_info'], 'masculine or feminine Ātmanepada (middle verb form) neuter gender')
        self.assertIn('black, dark', parsed['definition'])
        self.assertIn('raw_xml', parsed)

    def test_04_database_searches(self):
        # 1. Search by Devanagari
        res_dev = search_by_headword('कृष्ण')
        self.assertGreater(res_dev['count'], 0)
        self.assertEqual(res_dev['results'][0]['key_slp1'], 'kfzRa')

        # 2. Search by IAST
        res_iast = search_by_headword('kṛṣṇa')
        self.assertGreater(res_iast['count'], 0)
        self.assertEqual(res_iast['results'][0]['key_slp1'], 'kfzRa')

        # 3. Search by Loose ASCII
        res_ascii = search_by_headword('krishna')
        self.assertGreater(res_ascii['count'], 0)
        self.assertEqual(res_ascii['results'][0]['key_slp1'], 'kfzRa')

        # 4. Search by Loose ASCII "dharma"
        res_dharma = search_by_headword('dharma')
        self.assertGreater(res_dharma['count'], 0)
        self.assertEqual(res_dharma['results'][0]['key_slp1'], 'Darma')

    def test_05_english_fts_search(self):
        res_fts = search_english_fts('liberation', limit=5)
        self.assertGreater(res_fts['count'], 0)
        self.assertIn('liberation', res_fts['results'][0]['fts_snippet'].lower())

    def test_06_autocomplete(self):
        suggestions = autocomplete_headwords('krishn', limit=5)
        self.assertGreater(len(suggestions), 0)
        headwords = [s['slp1'] for s in suggestions]
        self.assertTrue(any(h.startswith('kfzR') for h in headwords))

    def test_07_api_health_endpoint(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['database'], 'connected')

    def test_08_api_metrics_endpoint(self):
        response = self.client.get('/metrics')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('memory_rss_mb', data)
        self.assertLess(data['memory_rss_mb'], 300.0) # Memory requirement check

    def test_09_api_define_endpoint(self):
        # Loose ASCII
        response = self.client.get('/api/v1/define/krishna')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(data['count'], 0)

        # Devanagari
        response_dev = self.client.get('/api/v1/define/कृष्ण')
        self.assertEqual(response_dev.status_code, 200)
        self.assertGreater(response_dev.json()['count'], 0)

    def test_10_api_transliterate_endpoint(self):
        response = self.client.get('/api/v1/transliterate?text=कृष्ण&to_scheme=iast')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['transliterated_text'], 'kṛṣṇa')


if __name__ == '__main__':
    unittest.main()

import os

from django.conf import settings
from django.test import TestCase
from elasticsearch import Elasticsearch

from crime_stats import index, load_crimes


TEST_INDEX = 'crimes_test'

es = Elasticsearch()


class TestCrimes(TestCase):
    @classmethod
    def setUpClass(cls):
        index.delete_index(es, TEST_INDEX)
        index.create_index(es, TEST_INDEX)
        filename = os.path.join(settings.DATA_DIR, 'crimes_2013.json')
        load_crimes.load_crimes(filename, es=es, index_name=TEST_INDEX)

    @classmethod
    def tearDownClass(cls):
        index.delete_index(es, TEST_INDEX)

    def test_it_works(self):
        self.assertTrue(True)

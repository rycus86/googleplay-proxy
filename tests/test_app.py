import os
import json

import unittest

from unittest_helper import get_api_client

import app


class AppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_api = app.api
        app.api = get_api_client()

    @classmethod
    def tearDownClass(cls):
        app.api = cls.original_api

    def setUp(self):
        app.app.testing = True
        self.client = app.app.test_client()

    def test_search_applications(self):
        response = self.client.get('/search/hu.rycus')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.charset, 'utf-8')

        applications = json.loads(response.data)

        self.assertIsNotNone(applications)
        self.assertGreater(len(applications), 0)

        for item in applications:
            self.assertIn('package_name', item)
            self.assertTrue(item.get('package_name').startswith('hu.rycus'))

            self._verify_item(item, simple=True)

    def test_get_application_details(self):
        response = self.client.get('/details/hu.rycus.tweetwear')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.charset, 'utf-8')

        details = json.loads(response.data)

        self.assertIsNotNone(details)

        self.assertIn('package_name', details)
        self.assertEqual(details.get('package_name'), 'hu.rycus.tweetwear')

        self._verify_item(details, simple=False)

        self.assertIn('description_html', details)
        self.assertIn('developer_name', details)
        self.assertIn('developer_website', details)
        self.assertIn('version_string', details)
        self.assertIn('recent_changes_html', details)

    def test_scraper_api(self):
        os.environ['API_TYPE'] = 'scraper'

        try:
            self.assertIsInstance(app.load_api(), app.Scraper)

        finally:
            del os.environ['API_TYPE']

    def _verify_item(self, item, simple):
        self._verify_basics(item)

        self.assertIn('images', item)
        self.assertGreater(len(item.get('images')), 0)

        for image in item.get('images'):
            self._verify_image(image, simple)

        self._verify_ratings(item)

    def _verify_basics(self, item):
        self.assertIn('title', item)
        self.assertIn('creator', item)
        self.assertIn('upload_date', item)
        self.assertIn('num_downloads', item)
        self.assertIn('version_code', item)
        self.assertIn('share_url', item)

    def _verify_image(self, image, simple):
        self.assertIn('type', image)
        self.assertIn('url', image)

        if not simple:
            self.assertIn('width', image)
            self.assertIn('height', image)
            self.assertIn('position', image)

    def _verify_ratings(self, item):
        self.assertIn('ratings', item)
        self.assertIn('stars', item.get('ratings'))
        self.assertIn('total', item.get('ratings'))
        self.assertIn('comments', item.get('ratings'))
        self.assertIn('count', item.get('ratings'))

        self.assertEqual(len(item.get('ratings').get('count')), 5)

        for star, count in item.get('ratings').get('count').items():
            self.assertGreaterEqual(int(star), 1)
            self.assertLessEqual(int(star), 5)

            self.assertGreaterEqual(int(count), 0)

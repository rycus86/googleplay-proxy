import os
import json
import unittest

import app


class AppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        details = AppTest._get_access_details()

        app.api = app.ApiClient(android_id=os.environ.get('ANDROID_ID', details.get('androidId')),
                                username=os.environ.get('GOOGLE_USERNAME', details.get('username')),
                                password=os.environ.get('GOOGLE_PASSWORD', details.get('password')))

    def setUp(self):
        app.app.testing = True
        self.client = app.app.test_client()

    @staticmethod
    def _get_access_details():
        directory = os.path.dirname(__file__) or '.'
        path = os.path.join(os.path.abspath(directory), '../../google-play-access.json')

        if os.path.exists(path):
            with open(path) as access:
                return json.load(access)

        return dict()

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

            self.assertIn('title', item)
            self.assertIn('creator', item)
            self.assertIn('upload_date', item)
            self.assertIn('num_downloads', item)
            self.assertIn('version_code', item)
            self.assertIn('share_url', item)

            self.assertIn('images', item)
            self.assertGreater(len(item.get('images')), 0)

            for image in item.get('images'):
                self.assertIn('type', image)
                self.assertIn('url', image)

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

    def test_get_application_details(self):
        response = self.client.get('/details/hu.rycus.tweetwear')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.charset, 'utf-8')

        details = json.loads(response.data)

        self.assertIsNotNone(details)

        self.assertIn('package_name', details)
        self.assertEqual(details.get('package_name'), 'hu.rycus.tweetwear')

        self.assertIn('title', details)
        self.assertIn('creator', details)
        self.assertIn('upload_date', details)
        self.assertIn('num_downloads', details)
        self.assertIn('version_code', details)
        self.assertIn('share_url', details)

        self.assertIn('description_html', details)
        self.assertIn('developer_name', details)
        self.assertIn('developer_website', details)
        self.assertIn('version_string', details)
        self.assertIn('recent_changes_html', details)

        self.assertIn('images', details)
        self.assertGreater(len(details.get('images')), 0)

        for image in details.get('images'):
            self.assertIn('type', image)
            self.assertIn('url', image)
            self.assertIn('width', image)
            self.assertIn('height', image)
            self.assertIn('position', image)

        self.assertIn('ratings', details)
        self.assertIn('stars', details.get('ratings'))
        self.assertIn('total', details.get('ratings'))
        self.assertIn('comments', details.get('ratings'))
        self.assertIn('count', details.get('ratings'))

        self.assertEqual(len(details.get('ratings').get('count')), 5)

        for star, count in details.get('ratings').get('count').items():
            self.assertGreaterEqual(int(star), 1)
            self.assertLessEqual(int(star), 5)

            self.assertGreaterEqual(int(count), 0)

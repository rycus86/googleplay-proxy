import os
import json
import unittest
from api import ApiClient, ApiLoginException


class ApiClientTest(unittest.TestCase):
    def setUp(self):
        details = self._get_access_details()

        self.api = ApiClient(android_id=os.environ.get('ANDROID_ID', details.get('androidId')),
                             username=os.environ.get('GOOGLE_USERNAME', details.get('username')),
                             password=os.environ.get('GOOGLE_PASSWORD', details.get('password')))

    @staticmethod
    def _get_access_details():
        directory = os.path.dirname(__file__) or '.'
        path = os.path.join(os.path.abspath(directory), '../../google-play-access.json')

        if os.path.exists(path):
            with open(path) as access:
                return json.load(access)

        return dict()

    def test_login(self):
        self.api.login()

        self.assertTrue(self.api.is_logged_in(), msg='Failed to log in')

    def test_login_failure(self):
        api = ApiClient(android_id='FAKE_ID', username='unknown@address.com', password='1234', max_login_retries=3)

        try:
            api.login()

            self.fail('Login should have failed')

        except ApiLoginException:
            pass

        self.assertFalse(api.is_logged_in(), msg='Expected not to be logged in')

    def test_search(self):
        results = self.api.search('hu.rycus')

        self.assertIsNotNone(results)
        self.assertGreater(len(results), 0)

        for item in results:
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
                self.assertGreaterEqual(star, 1)
                self.assertLessEqual(star, 5)

                self.assertGreaterEqual(count, 0)

    def test_details(self):
        item = self.api.get_details('hu.rycus.tweetwear')

        self.assertIsNotNone(item)

        self.assertIn('package_name', item)
        self.assertEqual(item.get('package_name'), 'hu.rycus.tweetwear')

        self.assertIn('title', item)
        self.assertIn('creator', item)
        self.assertIn('upload_date', item)
        self.assertIn('num_downloads', item)
        self.assertIn('version_code', item)
        self.assertIn('share_url', item)

        self.assertIn('description_html', item)
        self.assertIn('developer_name', item)
        self.assertIn('developer_website', item)
        self.assertIn('version_string', item)
        self.assertIn('recent_changes_html', item)

        self.assertIn('images', item)
        self.assertGreater(len(item.get('images')), 0)

        for image in item.get('images'):
            self.assertIn('type', image)
            self.assertIn('url', image)
            self.assertIn('width', image)
            self.assertIn('height', image)
            self.assertIn('position', image)

        self.assertIn('ratings', item)
        self.assertIn('stars', item.get('ratings'))
        self.assertIn('total', item.get('ratings'))
        self.assertIn('comments', item.get('ratings'))
        self.assertIn('count', item.get('ratings'))

        self.assertEqual(len(item.get('ratings').get('count')), 5)

        for star, count in item.get('ratings').get('count').items():
            self.assertGreaterEqual(star, 1)
            self.assertLessEqual(star, 5)

            self.assertGreaterEqual(count, 0)

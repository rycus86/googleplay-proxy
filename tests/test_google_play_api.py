import os
import time
import unittest
from unittest_helper import get_access_details

from googleplay_api.googleplay import GooglePlayAPI, LoginError


class GooglePlayApiTest(unittest.TestCase):
    api = GooglePlayAPI()

    @classmethod
    def setUpClass(cls):
        details = get_access_details()

        api = GooglePlayApiTest.api
        api.androidId = os.environ.get('ANDROID_ID', details.get('androidId'))

        last_error = None

        for _ in xrange(10):
            try:
                api.login(email=os.environ.get('GOOGLE_USERNAME', details.get('username')),
                          password=os.environ.get('GOOGLE_PASSWORD', details.get('password')))
                break

            except LoginError as err:
                last_error = err
                time.sleep(0.2)

        else:
            raise last_error

    def test_search(self):
        results = self.api.search('hu.rycus')

        self.assertTrue(hasattr(results, 'doc'), msg='Main doc object not found')
        self.assertGreater(len(results.doc), 0)

        document = results.doc[0]

        self.assertTrue(hasattr(document, 'child'), msg='Child object not found')
        self.assertGreater(len(document.child), 0)

        for child in document.child:
            self._verify_item(child, simple=True)

    def test_details(self):
        details = self.api.details('hu.rycus.watchface.triangular')

        self.assertTrue(hasattr(details, 'docV2'), msg='Main docV2 object not found')

        document = details.docV2

        self._verify_item(document, simple=False)
            
    def _verify_item(self, item, simple):
        for expected in ('title', 'creator', 'image', 'details', 'aggregateRating', 'shareUrl'):
            self.assertTrue(hasattr(item, expected),
                            msg='Result document does not contain the %s field' % expected)

        if not simple:
            self.assertTrue(hasattr(item, 'descriptionHtml'),
                            msg='Result document does not contain the descriptionHtml field')

        for image in item.image:
            for expected in ('imageType', 'imageUrl'):
                self.assertTrue(hasattr(image, expected),
                                msg='Image does not contain the %s field' % expected)

            if not simple:
                for expected in ('dimension', 'positionInSequence'):
                    self.assertTrue(hasattr(image, expected),
                                    msg='Image does not contain the %s field' % expected)

                dimension = image.dimension

                for expected in ('width', 'height'):
                    self.assertTrue(hasattr(dimension, expected),
                                    msg='Image dimension does not contain the %s field' % expected)

        details = item.details

        self.assertTrue(hasattr(details, 'appDetails'), msg='Result does not contain the appDetails object')

        app_details = details.appDetails

        for expected in ('packageName', 'uploadDate', 'numDownloads', 'versionCode'):
            self.assertTrue(hasattr(app_details, expected),
                            msg='App details do not contain the %s field' % expected)

        if not simple:
            for expected in ('developerName', 'versionString', 'developerWebsite', 'recentChangesHtml'):
                self.assertTrue(hasattr(app_details, expected),
                                msg='App details do not contain the %s field' % expected)

        rating = item.aggregateRating

        for expected in ('starRating', 'ratingsCount', 'commentCount',
                         'oneStarRatings', 'twoStarRatings', 'threeStarRatings',
                         'fourStarRatings', 'fiveStarRatings'):
            self.assertTrue(hasattr(rating, expected),
                            msg='App rating does not contain the %s field' % expected)

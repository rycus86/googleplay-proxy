import json
import time
import unittest
from googleplay_api.googleplay import GooglePlayAPI, LoginError


# pip install git+git://github.com/NeroBurner/googleplay-api@master


class TestGooglePlayApi(unittest.TestCase):
    api = GooglePlayAPI()

    @classmethod
    def setUpClass(cls):
        with open('../../google-play-access.json') as access:
            details = json.load(access)

        api = TestGooglePlayApi.api
        api.androidId = details.get('androidId')

        last_error = None

        for _ in xrange(10):
            try:
                api.login(details.get('username'), details.get('password'))
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
            for expected in ('title', 'creator', 'image', 'details', 'aggregateRating', 'shareUrl'):
                self.assertTrue(hasattr(child, expected),
                                msg='Result document does not contain the %s field' % expected)

            for image in child.image:
                for expected in ('imageType', 'imageUrl'):
                    self.assertTrue(hasattr(image, expected),
                                    msg='Image does not contain the %s field' % expected)

            details = child.details

            self.assertTrue(hasattr(details, 'appDetails'), msg='Result does not contain the appDetails object')

            app_details = details.appDetails

            for expected in ('packageName', 'uploadDate', 'numDownloads', 'versionCode'):
                self.assertTrue(hasattr(app_details, expected),
                                msg='App details do not contain the %s field' % expected)

            rating = child.aggregateRating

            for expected in ('starRating', 'ratingsCount', 'commentCount',
                             'oneStarRatings', 'twoStarRatings', 'threeStarRatings',
                             'fourStarRatings', 'fiveStarRatings'):
                self.assertTrue(hasattr(rating, expected),
                                msg='App rating does not contain the %s field' % expected)

    def test_details(self):
        details = self.api.details('hu.rycus.watchface.triangular')

        self.assertTrue(hasattr(details, 'docV2'), msg='Main docV2 object not found')

        document = details.docV2

        for expected in ('title', 'creator', 'image', 'details', 'aggregateRating', 'shareUrl',
                         'descriptionHtml'):
            self.assertTrue(hasattr(document, expected),
                            msg='Result document does not contain the %s field' % expected)

        for image in document.image:
            for expected in ('imageType', 'imageUrl', 'Dimension', 'positionInSequence'):
                self.assertTrue(hasattr(image, expected),
                                msg='Image does not contain the %s field' % expected)

            dimension = image.Dimension

            for expected in ('width', 'height'):
                self.assertTrue(hasattr(dimension, expected),
                                msg='Image dimension does not contain the %s field' % expected)

        details = document.details

        self.assertTrue(hasattr(details, 'appDetails'), msg='Result does not contain the appDetails object')

        app_details = details.appDetails

        for expected in ('packageName', 'uploadDate', 'numDownloads', 'versionCode',
                         'developerName', 'versionString', 'developerWebsite', 'recentChangesHtml'):
            self.assertTrue(hasattr(app_details, expected),
                            msg='App details do not contain the %s field' % expected)

        rating = document.aggregateRating

        for expected in ('starRating', 'ratingsCount', 'commentCount',
                         'oneStarRatings', 'twoStarRatings', 'threeStarRatings',
                         'fourStarRatings', 'fiveStarRatings'):
            self.assertTrue(hasattr(rating, expected),
                            msg='App rating does not contain the %s field' % expected)

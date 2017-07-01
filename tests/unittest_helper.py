import os
import json

from api import ApiClient, LoginError


def get_api_client(unauthorized=False):
    if os.environ.get('INTEGRATION_TESTS'):
        return get_real_api_client()

    class MockResponse(dict):
        def __init__(self, *args, **kwargs):
            super(MockResponse, self).__init__(*args, **kwargs)

        def __getattr__(self, item):
            return self.get(item)

    _md = MockResponse

    class MockApi(object):
        def login(self, *args, **kwargs):
            if unauthorized:
                raise LoginError('Requested login failure')

        def search(self, prefix):
            return _md({
                'doc': [
                    _md({
                        'child': [
                            self._create_mock('%s.app1' % prefix),
                            self._create_mock('%s.app2' % prefix),
                            self._create_mock('%s.app3' % prefix)
                        ]
                    })
                ]
            })

        def details(self, package):
            return _md({
                'docV2': self._create_mock(package)
            })

        def _create_mock(self, package):
            return _md({
                'details': _md({
                    'appDetails': _md({
                        'packageName': package
                    })
                }),
                'image': [
                    _md({
                        'type': 1,
                        'imageUrl': 'http://sample.com/image-1.png',
                        'dimension': _md({
                            'width': 120,
                            'height': 100,
                            'position': 1
                        })
                    })
                ],
                'aggregateRating': _md({
                    'oneStarRatings': 10,
                    'twoStarRatings': 20,
                    'threeStarRatings': 30,
                    'fourStarRatings': 40,
                    'fiveStarRatings': 50
                })
            })

    class MockApiClient(ApiClient):
        def __init__(self):
            super(MockApiClient, self).__init__()
            self._api = MockApi()

    return MockApiClient()


def get_real_api_client():
    details = get_access_details()

    return ApiClient(android_id=os.environ.get('ANDROID_ID', details.get('androidId')),
                     username=os.environ.get('GOOGLE_USERNAME', details.get('username')),
                     password=os.environ.get('GOOGLE_PASSWORD', details.get('password')))


def get_access_details():
    directory = os.path.dirname(__file__) or '.'
    path = os.path.join(os.path.abspath(directory), '../google-play-access.json')

    if os.path.exists(path):
        with open(path) as access:
            return json.load(access)

    return dict()

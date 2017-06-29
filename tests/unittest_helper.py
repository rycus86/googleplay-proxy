import os
import json

from api import ApiClient, ApiLoginException


def get_api_client(unauthorized=False):
    class MockResponse(dict):
        def __getattr__(self, item):
            return self.get(item)

    _md = MockResponse

    class MockApi(object):
        def search(self, prefix):
            return _md({
                'doc': list()
            })

        def details(self, package):
            return _md({
                'docV2': _md({
                    'details': _md({
                        'appDetails': _md()
                    }),
                    'image': list(),
                    'aggregateRating': _md()
                })
            })

    class MockApiClient(ApiClient):
        def __init__(self, **kwargs):
            self._api = MockApi()
            self._logged_in = False

        def login(self):
            if unauthorized:
                raise ApiLoginException('Failed to log in: Unauthorized')

            self._logged_in = True

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

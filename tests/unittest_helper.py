import os
import json

from api import ApiClient


def get_api_client():
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

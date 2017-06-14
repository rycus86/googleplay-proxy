import time
import logging
from threading import Lock
from functools import wraps
from googleplay_api.googleplay import GooglePlayAPI, LoginError, DecodeError

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(module)s.%(funcName)s - %(message)s')
logger = logging.getLogger('googleplay-proxy')
logger.setLevel(logging.INFO)


def _with_login(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.is_logged_in():
            self.login()

        try:
            return method(self, *args, **kwargs)

        except DecodeError as err:
            logger.warn('Failed to decode the response, possible authentication token issue: %s', err)

            self.login()
            return method(self, *args, **kwargs)

    return wrapper


class ApiLoginException(BaseException):
    def __init__(self, cause):
        super(ApiLoginException, self).__init__(cause)


class ApiItem(dict):
    def __setattr__(self, key, value):
        self[key] = value


class ApiClient(object):
    def __init__(self, android_id=None, username=None, password=None,
                 auth_token=None, proxy=None, max_login_retries=10, language=None, debug=False):

        self._api = GooglePlayAPI(android_id, language, debug)

        self._username = username
        self._password = password
        self._auth_token = auth_token
        self._proxy = proxy
        self._max_login_retries = max_login_retries

        self._login_lock = Lock()
        self._logged_in = False

    def is_logged_in(self):
        return self._logged_in

    def login(self):
        self._logged_in = False

        with self._login_lock:
            logger.info('Executing login')

            login_error = None

            for _ in xrange(self._max_login_retries):
                try:
                    self._api.login(self._username, self._password, self._auth_token, self._proxy)
                    self._logged_in = True
                    break

                except LoginError as err:
                    login_error = err
                    time.sleep(0.2)

            else:
                logger.error('Failed to log in: %s', login_error)
                raise ApiLoginException(login_error)

    @_with_login
    def search(self, package_prefix):
        logger.info('Searching for %s', package_prefix)

        results = list()
        response = self._api.search(package_prefix)

        if len(response.doc):
            document = response.doc[0]

            for child in document.child:
                package_name = child.details.appDetails.packageName

                if not package_name.startswith(package_prefix):
                    continue

                item = self._extract_api_item(child)

                results.append(item)

        return results

    @_with_login
    def get_details(self, package_name):
        logger.info('Fetching details for %s', package_name)

        details = self._api.details(package_name)
        return self._extract_api_item(details.docV2)

    @staticmethod
    def _extract_api_item(api_object):
        details = api_object.details.appDetails

        item = ApiItem()

        item.package_name = details.packageName
        item.title = api_object.title
        item.creator = api_object.creator
        item.upload_date = details.uploadDate
        item.num_downloads = details.numDownloads
        item.version_code = details.versionCode
        item.share_url = api_object.shareUrl

        if hasattr(api_object, 'descriptionHtml'):
            item.description_html = api_object.descriptionHtml

        if hasattr(details, 'developerName'):
            item.developer_name = details.developerName
        if hasattr(details, 'developerWebsite'):
            item.developer_website = details.developerWebsite
        if hasattr(details, 'versionString'):
            item.version_string = details.versionString
        if hasattr(details, 'recentChangesHtml'):
            item.recent_changes_html = details.recentChangesHtml

        images = list()

        for image_object in api_object.image:
            image = ApiItem()

            image.type = image_object.imageType
            image.url = image_object.imageUrl

            if hasattr(image_object, 'dimension'):
                image.width = image_object.dimension.width
                image.height = image_object.dimension.height

            if hasattr(image_object, 'positionInSequence'):
                image.position = image_object.positionInSequence

            images.append(image)

        item.images = images

        item.ratings = {
            'stars': api_object.aggregateRating.starRating,
            'total': api_object.aggregateRating.ratingsCount,
            'comments': api_object.aggregateRating.commentCount,
            'count': {
                1: api_object.aggregateRating.oneStarRatings,
                2: api_object.aggregateRating.twoStarRatings,
                3: api_object.aggregateRating.threeStarRatings,
                4: api_object.aggregateRating.fourStarRatings,
                5: api_object.aggregateRating.fiveStarRatings
            }
        }

        return item

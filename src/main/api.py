import time
import logging
from googleplay_api.googleplay import GooglePlayAPI, LoginError


logger = logging.getLogger('googleplay-proxy')


class ApiClient(object):

    def __init__(self, androidId=None, lang=None, debug=False):
        self._api = GooglePlayAPI(androidId, lang, debug)

    def login(self, email=None, password=None, authSubToken=None, proxy=None, max_retries=10):
        logger.info('Executing login')

        login_error = None

        for _ in xrange(max_retries):
            try:
                self._api.login(email, password, authSubToken, proxy)
                break

            except LoginError as err:
                login_error = err
                time.sleep(0.2)

        else:
            logger.error('Failed to log in: %s', login_error)
            raise login_error

    def search(self, query):
        logger.info('Searching for %s', query)

        results = list()
        response = self._api.search(query)
        
        if len(response.doc):
            document = response.doc[0]

            for child in document.child:
                item = {
                    key: getattr(child, key)
                    for key in ('title', 'creator', 'shareUrl')
                }
                
                images = list()

                for image in child.image:
                    images.append({
                        'type': image.imageType,
                        'url': image.imageUrl
                    })

                details = child.details.appDetails

                item.update({
                    key: getattr(details, key)
                    for key in ('packageName', 'uploadDate', 'numDownloads', 'versionCode')
                })

                item['ratings'] = {
                    key: getattr(child.aggregateRating, key)
                    for key in ('starRating', 'ratingsCount', 'commentCount',
                                'oneStarRatings', 'twoStarRatings', 'threeStarRatings',
                                'fourStarRatings', 'fiveStarRatings')
                }

                results.append(item)

        return results

    def get_details(self, package_name):
        logger.info('Fetching details for %s', package_name)

        result = dict()

        details = self._api.details(package_name)
        # TODO error handling

        document = details.docV2

        result.update({
            key: getattr(details, key)
            for key in ('title', 'creator', 'shareUrl', 'descriptionHtml')
        })

        for image in document.image:
            pass

        return result


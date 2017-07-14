import logging
import os
import re
import tempfile
import time
from hashlib import md5

from bs4 import BeautifulSoup as soup
from urllib import quote_plus
from urllib2 import urlopen

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(module)s.%(funcName)s - %(message)s')
logger = logging.getLogger('googleplay-proxy')
logger.setLevel(logging.INFO)


def _read(path):
    with open(path, 'r') as input_file:
        return input_file.read()


class Scraper(object):
    BASE_URL = 'https://play.google.com'

    PATH_SEARCH = '/store/search?q={package_prefix}&c=apps'
    PATH_DEVELOPER = '/store/apps/developer?id={developer_name}'
    PATH_DETAILS = '/store/apps/details?id={package_name}'

    def __init__(self, cache_max_age=24 * 60 * 60):
        self.cache_max_age = cache_max_age

    def _fetch(self, url):
        url = self._url(url)

        hashed = md5()
        hashed.update(url)
        filename = hashed.hexdigest()

        path = os.path.join(tempfile.gettempdir(), '%s.content' % filename)

        if os.path.exists(path):
            last_modified = os.path.getmtime(path)

            if time.time() < last_modified + self.cache_max_age:
                logger.info('URL found in cache: %s', url)

                with open(path) as cache_file:
                    return cache_file.read()

        logger.info('Fetching from URL: %s ...', url)

        data = urlopen(url).read()

        with open(path, 'w') as cache_file:
            cache_file.write(data)

        return data

    def _url(self, string):
        if '://' in string:
            return string

        if string.startswith('//'):
            return 'https:%s' % string

        if string.startswith('/'):
            return '%s%s' % (self.BASE_URL, string)

        return string

    def search(self, package_prefix):
        return list(self.scrape_search(package_prefix))

    def scrape_search(self, package_prefix):
        logger.info('Searching with package prefix: %s', package_prefix)

        html = soup(self._fetch(self.PATH_SEARCH.format(package_prefix=package_prefix)), 'html.parser')

        for elem in html.find_all('div', class_='card', attrs={'data-docid': True}):
            package_name = elem.attrs.get('data-docid', '')

            if not package_name.startswith(package_prefix):
                continue

            yield self._fetch_from_search_result(elem)

    def developer(self, developer_name):
        return list(self.scrape_developer(developer_name))

    def scrape_developer(self, developer_name):
        logger.info('Searching for developer: %s', developer_name)

        html = soup(self._fetch(self.PATH_DEVELOPER.format(developer_name=quote_plus(developer_name))), 'html.parser')

        for elem in html.find_all('div', class_='card', attrs={'data-docid': True}):
            yield self._fetch_from_search_result(elem)

    def _fetch_from_search_result(self, elem):
        package_name = elem.attrs.get('data-docid', '')
        developer = elem.find('a', class_='subtitle', attrs={'title': True})
        cover_image = elem.find('img', class_='cover-image')

        item = {
            'package_name': package_name,
            'share_url': self._url(elem.find('a', class_='card-click-target').attrs.get('href')),
            'title': elem.find('a', class_='title', attrs={'title': True}).get('title'),
            'creator': developer.get('title'),

            'description_html': '\n\n'.join(re.subn(r'\s{2,}', r' ',
                                                    unicode(child.text if hasattr(child, 'text') else child),
                                                    re.MULTILINE)[0]
                                            for child in elem.find('div', class_='description'))
                                      .strip().replace('\n', '<br/>'),

            'cover_image': {
                'main': self._url(cover_image.get('src')),
                'small': self._url(cover_image.get('data-cover-small')),
                'large': self._url(cover_image.get('data-cover-large'))
            }
        }

        return item

    def get_details(self, package_name):
        return self.scrape_details(package_name)

    def scrape_details(self, package_name):
        logger.info('Fetching details for: %s', package_name)

        html = soup(self._fetch(self.PATH_DETAILS.format(package_name=package_name)), 'html.parser')

        elem = html.find('div', class_='main-content')

        if not elem or not elem.find(attrs={'data-docid': package_name}):
            return

        developer = elem.find('div', itemprop='author').find('a', class_='primary')
        reviews = elem.find('div', class_='reviews')
        whats_new = elem.find('div', class_='whatsnew')

        item = {
            'package_name': package_name,
            'cover_image': self._url(elem.find('img', class_='cover-image').get('src')),
            'title': elem.find('div', class_='document-title').text.strip(),
            'share_url': self._url(html.find('link', rel='canonical').get('href')),

            'creator': developer.find('span', itemprop='name').text.strip(),
            'developer_name': developer.find('span', itemprop='name').text.strip(),
            'developer_website': elem.find('a', class_='dev-link', href=re.compile('^https?://.*')).get('href'),

            'description_html': ''.join(re.subn('\s{2,}', r' ',
                                                unicode(child),
                                                re.MULTILINE)[0]
                                        for child in elem.select_one('div.show-more-content div:nth-of-type(1)')),

            'images': [
                {
                    'url': self._url(img.get('src'))
                } for img in elem.find_all('img', class_='full-screenshot')
            ],

            'genres': [genre.text.strip() for genre in elem.find_all('span', itemprop='genre')],

            'ratings': {
                'stars': float(reviews.find('meta', itemprop='ratingValue').get('content')),
                'total': int(reviews.find('meta', itemprop='ratingCount').get('content')),
                'count': {
                    num: int(reviews.find('div', class_=('rating-bar-container %s' % as_string))
                             .find('span', class_='bar-number')
                             .text.strip())
                    for (num, as_string) in [(5, 'five'), (4, 'four'), (3, 'three'),
                                             (2, 'two'), (1, 'one')]
                }
            },

            'recent_changes_html': '<br/>'.join(re.subn(r'\s{2,}', r' ', child.text, re.MULTILINE)[0]
                                                for child in whats_new.find_all('div', class_='recent-change')),

            'upload_date': elem.find('div', itemprop='datePublished').text.strip(),
            'download_count': elem.find('div', itemprop='numDownloads').text.strip()
        }

        return item

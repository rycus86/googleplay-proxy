import os
from bs4 import BeautifulSoup as soup


def _read(path):
    with open(path, 'r') as input_file:
        return input_file.read()


class Scraper(object):
    def __init__(self):
        pass

    def _fetch(self, url):
        return _read(url)  # TODO

    def search(self, package_prefix):
        html = soup(self._fetch('/tmp/gplay/search.html'))  # TODO

        for elem in html.findAll('div', attrs={'data-docid': True}):
            if 'card' not in elem['class']:
                continue

            package_name = elem.attrs.get('data-docid', '')

            if not package_name.startswith(package_prefix):
                continue
            
            item = {
                'package_name': package_name,
                'url': elem.find('a', class_='card-click-target').attrs.get('href'),  # TODO
                'title': elem.find('a', class_='title', attrs={'title': True}).get('title'),
                'developer': {
                    'name': elem.find('a', class_='subtitle', attrs={'title': True}).get('title'),
                    'url': elem.find('a', class_='subtitle', attrs={'title': True}).get('href')
                },
                'description': elem.find('div', class_='description').text.strip()
            }

            cover_image = elem.find('img', class_='cover-image')
            
            if cover_image:
                item['cover_image'] = {
                    'main': cover_image['src'],
                    'small': cover_image['data-cover-small'],
                    'large': cover_image['data-cover-large']
                }

            yield item

    def developer(self):
        pass

    def details(self, package_name):
        html = soup(self._fetch('/tmp/gplay/details.html'))  # TODO
        
        elem = html.find('div', class_='details-wrapper', attrs={'data-docid': package_name})
        
        if not elem:
            return

        item = {
            'package_name': package_name,
            'cover-image': elem.find('img', class_='cover-image').get('src'),
            'title': elem.find('div', class_='document-title').text.strip(),
        }

        developer = elem.find('div', itemprop='author').find('a', class_='primary')

        if developer:
            item['developer'] = {
                'name': developer.find('span', itemprop='name').text.strip(),
                'url': developer.get('href')
            }

        genre = elem.find('span', itemprop='genre')

        if genre:
            item['genre'] = {
                'name': genre.text.strip(),
                'url': genre.parent.get('href')
            }

        return item


if __name__ == '__main__':
    # self-test
#    for result in  Scraper().search('hu.rycus'):
#        print result
    print Scraper().details('hu.rycus.watchface.stringtheory')


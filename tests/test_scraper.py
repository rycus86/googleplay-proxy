import unittest

import scraper


class ScraperTest(unittest.TestCase):
    def setUp(self):
        self.scraper = scraper.Scraper(cache_max_age=0)

        self.original_urlopen = scraper.urlopen
        scraper.urlopen = self._mock_urlopen

        self.opened_url = None
        self.response_data = None

    def tearDown(self):
        scraper.urlopen = self.original_urlopen

    def _mock_urlopen(self, url):
        self.opened_url = url

        _self = self

        class MockResponse(object):
            def read(self):
                return _self.response_data

        return MockResponse()

    def test_search(self):
        self.response_data = """
        <html><body>
        <div class="card" data-docid="mock.package.app1">
            <a class="subtitle" title="Developer1">Developer1</a>
            <a class="card-click-target" href="http://share.url/app1">Link</a>
            <a class="title" title="App1">App1</a>
            <div class="description">
                Description for<br/>
                application1
            </div>
            <img class="cover-image" src="image1-main"
                 data-cover-small="image1-small" data-cover-large="image1-large"/>
        </div>
        <div class="card" data-docid="mock.package.app2">
            <a class="subtitle" title="Developer2">Developer2</a>
            <a class="card-click-target" href="http://share.url/app2">Link</a>
            <a class="title" title="App2">App2</a>
            <div class="description">
                Description for<br/>
                application2
            </div>
            <img class="cover-image" src="image2-main"
                 data-cover-small="image2-small" data-cover-large="image2-large"/>
        </div>
        <div class="card" data-docid="different.package.app3"></div>
        </body></html>
        """

        result = self.scraper.search('mock.package')

        self.assertEqual(
            self.opened_url, 'https://play.google.com/store/search?q=mock.package&c=apps'
        )

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)

        for idx in range(2):
            item, index = result[idx], idx + 1

            self.assertEqual(item['package_name'], 'mock.package.app%d' % index)
            self.assertEqual(item['share_url'], 'http://share.url/app%d' % index)
            self.assertEqual(item['title'], 'App%d' % index)
            self.assertEqual(item['creator'], 'Developer%d' % index)
            self.assertEqual(item['cover_image']['main'], 'image%d-main' % index)
            self.assertEqual(item['cover_image']['small'], 'image%d-small' % index)
            self.assertEqual(item['cover_image']['large'], 'image%d-large' % index)
            self.assertEqual(
                item['description_html'],
                'Description for<br/><br/><br/><br/> application%d' % index
            )

    def test_developer(self):
        self.response_data = """
        <html><body>
        <div class="card" data-docid="mock.package.app1">
            <a class="subtitle" title="Test Dev">Test Dev</a>
            <a class="card-click-target" href="http://share.url/app1">Link</a>
            <a class="title" title="App1">App1</a>
            <div class="description">
                Description for<br/>
                application1
            </div>
            <img class="cover-image" src="image1-main"
                 data-cover-small="image1-small" data-cover-large="image1-large"/>
        </div>
        <div class="card" data-docid="mock.package.app2">
            <a class="subtitle" title="Test Dev">Test Dev</a>
            <a class="card-click-target" href="http://share.url/app2">Link</a>
            <a class="title" title="App2">App2</a>
            <div class="description">
                Description for<br/>
                application2
            </div>
            <img class="cover-image" src="image2-main"
                 data-cover-small="image2-small" data-cover-large="image2-large"/>
        </div>
        </body></html>
        """

        result = self.scraper.developer('Test Dev')

        self.assertEqual(
            self.opened_url, 'https://play.google.com/store/apps/developer?id=Test+Dev'
        )

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)

        for idx in range(2):
            item, index = result[idx], idx + 1

            self.assertEqual(item['package_name'], 'mock.package.app%d' % index)
            self.assertEqual(item['share_url'], 'http://share.url/app%d' % index)
            self.assertEqual(item['title'], 'App%d' % index)
            self.assertEqual(item['creator'], 'Test Dev')
            self.assertEqual(item['cover_image']['main'], 'image%d-main' % index)
            self.assertEqual(item['cover_image']['small'], 'image%d-small' % index)
            self.assertEqual(item['cover_image']['large'], 'image%d-large' % index)
            self.assertEqual(
                item['description_html'],
                'Description for<br/><br/><br/><br/> application%d' % index
            )

    def test_get_details(self):
        self.response_data = """
        <html><head>
            <link rel="canonical" href="http://share.url"/>
        </head><body>
        <div class="main-content">
            <meta data-docid="mock.package.app"/>
            <span itemprop="genre">Genre 1</span>
            <span itemprop="genre">Genre 2</span>
            <div class="document-title">App Title</div>
            <div itemprop="author">
                <a class="primary"><span itemprop="name">Developer Name</span></a>
                <a class="dev-link" href="https://developer.site">Dev Site</a>
            </div>
            <img class="cover-image" src="//cover.image"/>
            <img class="full-screenshot" src="http://screenshot.image"/>
            <div class="show-more-content">
                <div>App Description</div>
            </div>
            <div class="reviews">
                <meta itemprop="ratingValue" content="3.2"/>
                <meta itemprop="ratingCount" content="42"/>
                <div class="rating-bar-container one">
                    <span class="bar-number">10</span>
                </div>
                <div class="rating-bar-container two">
                    <span class="bar-number">20</span>
                </div>
                <div class="rating-bar-container three">
                    <span class="bar-number">30</span>
                </div>
                <div class="rating-bar-container four">
                    <span class="bar-number">40</span>
                </div>
                <div class="rating-bar-container five">
                    <span class="bar-number">50</span>
                </div>
            </div>
            <div class="whatsnew">
                <div class="recent-change">
                    A recent
                    change
                </div>
                <div class="recent-change">
                    Another change
                </div>
            </div>
            <div itemprop="datePublished">PublishDate</div>
            <div itemprop="numDownloads">DownloadCount</div>
        </div>
        </body></html>
        """

        result = self.scraper.get_details('mock.package.app')
        
        self.assertEqual(
            self.opened_url, 'https://play.google.com/store/apps/details?id=mock.package.app'
        )

        self.assertIsNotNone(result)

        self.assertEqual(result['package_name'], 'mock.package.app')
        self.assertEqual(result['cover_image'], 'https://cover.image')
        self.assertEqual(result['title'], 'App Title')
        self.assertEqual(result['share_url'], 'http://share.url')
        self.assertEqual(result['creator'], 'Developer Name')
        self.assertEqual(result['developer_name'], 'Developer Name')
        self.assertEqual(result['developer_website'], 'https://developer.site')
        self.assertEqual(result['description_html'], 'App Description')
        self.assertEqual(result['images'], [{'url': 'http://screenshot.image'}])
        self.assertEqual(result['genres'], ['Genre 1', 'Genre 2'])
        self.assertEqual(result['ratings']['stars'], 3.2)
        self.assertEqual(result['ratings']['total'], 42)
        self.assertEqual(result['upload_date'], 'PublishDate')
        self.assertEqual(result['download_count'], 'DownloadCount')
        self.assertEqual(
            result['recent_changes_html'].strip(),
            'A recent change <br/> Another change'
        )

        for rating in range(1, 6):
            self.assertEqual(result['ratings']['count'][rating], rating * 10)


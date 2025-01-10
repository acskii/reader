"""
This script contains all code relating to the web-scraping aspect of this project.
It contains classes of each supported website that houses methods that extract data from webpages.
It is heavily based on parsing through HTML and JavaScript to scrape data.
An extractor class may not function if the website associated has changed its layout.
"""

import re
from ..utils.base import Extractor
from ..utils.containers import *

TIMEOUT = 3         # Seconds to wait for request response
REQUEST_HEADERS = {
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:50.0) Gecko/20100101 Firefox/50.0',
    # Accept
}

class BatoExtractor(Extractor):
    def __init__(self):
        super().__init__()
        self.website = '1'
        self.website_name = 'BATO.TO'
        self.home_page_url = 'https://bato.to'
        self.search_page_url = 'https://bato.to/search?word=:;&page=:*'
        self.logo = 'https://bato.to/amsta/img/batoto/favicon.ico?v0'

    def last_search_page(self, url):
        document = self.load_document(self.load_response(url))

        if document is not None:
            pages = list()
            for link in document.xpath("//a/@href"):
                regex = re.search('page=(\d+)$', link)
                if regex:
                    pages.append(int(regex.groups()[0]))

            return max(pages) if len(pages) > 1 else 1
        return 1

    async def parse_search(self, url):
        document = self.load_document(self.load_response(url))
        results = dict()

        if document is not None:
            for index, search_item in enumerate(document.xpath(
                    "//div[contains(@class, 'series') or contains(@id, 'series')]/div[contains(@class, 'item')][./a]")):
                result = SearchResult()
                result.icon = search_item.xpath("./a/img/@src")[0]
                result.link = f"{self.home_page_url}{search_item.xpath('./a/@href')[0]}"
                result.title = search_item.xpath(".//div[contains(@class, 'item')]/a[contains(@class, 'title')]")[
                    0].text_content()

                for container in search_item.xpath(".//div[contains(@class, 'item')][./span or ./u or ./b]"):
                    result.add_info(
                        InfoNode(
                            [''.join([s for s in container.text_content() if '\n' not in s])]
                        )
                    )

                results[index] = result

        return results

    async def parse_desc(self, url):
        document = self.load_document(
            self.load_response(
                self.standardise_url(url)
            )
        )
        results = SeriesResult()

        if document is not None:
            alternate_title = document.xpath("//div[contains(@class, 'alias')]")
            titles = ' '.join([title.strip() for alt_title in alternate_title[0].xpath(".//text()") for title in
                               alt_title.strip().split('\n')])
            # A buttload of string manipulation here, any performance bugs might linger here :)
            results.add_info(InfoNode([titles]))

            # Getting information in description
            for div in document.xpath("//div[contains(@class, 'attr')]"):
                for container in div.xpath("./div[contains(@class, 'attr')]"):
                    results.add_info(
                        InfoNode([t.text for t in container.iter() if
                                  t.text and '\n' not in t.text and 'show the remaining' not in t.text.lower()])
                    )

            # Getting chapters
            for a in document.xpath("//div[contains(@class, 'main')]/div/a"):
                results.add_chapter(
                    ChapterNode(f"{self.home_page_url}{a.xpath('@href')[0]}", a.text_content())
                )

            # Getting summary
            results.summary = ''.join(
                [t for t in document.xpath("//div[contains(@class, 'limit')]/text()") if '\n' not in t])
            results.title = ''.join(document.xpath("//div[contains(@class, 'title')]//text()"))
            results.thumbnail = document.xpath("//div[contains(@class, 'cover')][./img]/img/@src")[0]
            results.website = self.website_name
            results.website_icon = self.logo
        return results

    async def parse_chapter(self, url):
        document = self.load_document(self.load_response(url))

        if document is not None:
            for script in document.xpath("//script/text()"):
                regex = re.search("const\s*imgHttps\s*=\s*(\[.+\])", script)

                if regex:
                    return ChapterResult(
                        dict(
                            enumerate(regex.groups()[0].strip('[]').replace('"', '').split(','), 1)
                        )
                    )
        return ChapterResult({})
        # .re("const\s*imgHttps\s*=\s*(\[.+\])")

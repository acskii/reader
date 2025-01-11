"""
This script contains all code relating to the web-scraping aspect of this project.
It contains classes of each supported website that houses methods that extract data from webpages.
It is heavily based on parsing through HTML and JavaScript to scrape data.
An extractor class may not function if the website associated has changed its layout.
"""

#
#
#   STANTARDISE URLS IN EXTRACTOR
#
#


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
        document = self.load_document(self.load_response(url, REQUEST_HEADERS, TIMEOUT))

        if document is not None:
            pages = list()
            for link in document.xpath("//a/@href"):
                regex = re.search('page=(\d+)$', link)
                if regex:
                    pages.append(int(regex.groups()[0]))

            return max(pages) if len(pages) > 1 else 1
        return 1

    async def parse_search(self, url):
        document = self.load_document(self.load_response(url, REQUEST_HEADERS, TIMEOUT))
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
        document = self.load_document(self.load_response(url, REQUEST_HEADERS, TIMEOUT))
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
        document = self.load_document(self.load_response(url, REQUEST_HEADERS, TIMEOUT))

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

class MangaDexExtractor(Extractor):
    def __init__(self):
        super().__init__()
        self.website = '2'
        self.website_name = 'MangaDex'
        self.home_page_url = 'https://mangadex.org'
        self.search_page_url = ':;'
        self.api_call_url = 'https://api.mangadex.org'
        self.api_cover_url = 'https://mangadex.org/covers'
        self.logo = 'https://mangadex.org/img/brand/mangadex-logo.svg'

    def last_search_page(self, response):
        return 1

    def standardise_url(self, url: str):
        regex = re.search(f"{self.home_page_url}/title/(.+)/", url)

        if regex is not None:
            return regex.group(1)
        else:
            return None

    async def parse_search(self, url):
        url = self.standardise_url(url)
        results = dict()

        # API Calls babbbbyyyy :)
        for index, detail in enumerate(self.load_response(f"{self.api_call_url}/manga", params={"title": url, "limit": 20, "includes[]": "cover_art"}).json()["data"]):
            result = SearchResult()
            attrs = detail['attributes']
            result.title = attrs['title']['en']

            # Alt titles
            result.add_info(InfoNode([attr['en'] for attr in attrs['altTitles'] if 'en' in attr]))
            # Original Language
            result.add_info(InfoNode(["Original Language: ", attrs['originalLanguage'].upper()]))
            # Year
            result.add_info(InfoNode(["Year: ", str(attrs['year'])]))
            # Status
            result.add_info(InfoNode(["Status: ", attrs['status']]))
            # Tags
            tags = ["Tags:"]
            tags.extend([tag['attributes']['name'].get('en', '') for tag in attrs['tags']])
            result.add_info(InfoNode(tags))
            # Description
            result.add_info(InfoNode([attrs['description'].get('en', '')]))

            result.icon = f"{self.api_cover_url}/{detail['id']}/{[r['attributes']['fileName'] for r in detail['relationships'] if r['type'] == 'cover_art'][0]}.{256}.jpg"
            result.link = detail['id']

            results[index] = result

        return results

    async def parse_desc(self, url):
        url = self.standardise_url(url)
        results = SeriesResult()

        series_data = self.load_response(f"{self.api_call_url}/manga/{url}", REQUEST_HEADERS, TIMEOUT, params={"includes[]": "cover_art"}).json()["data"]
        attrs = series_data["attributes"]
        # Original Language
        results.add_info(InfoNode(["Original Language: ", attrs['originalLanguage'].upper()]))
        # Year
        results.add_info(InfoNode(["Year: ", str(attrs['year'])]))
        # Status
        results.add_info(InfoNode(["Status: ", attrs['status']]))
        # Tags
        tags = ["Tags:"]
        tags.extend([tag['attributes']['name'].get('en', '') for tag in attrs['tags']])
        results.add_info(InfoNode(tags))
        # Description
        results.summary = attrs["description"].get("en", '')
        # Series title
        results.title = attrs["title"].get("en", '')
        # Thumbnail
        results.thumbnail = f"{self.api_cover_url}/{url}/{[r['attributes']['fileName'] for r in series_data['relationships'] if r['type'] == 'cover_art'][0]}.{256}.jpg"

        for index, detail in enumerate(self.load_response(f"{self.api_call_url}/manga/{url}/feed",
                                                          REQUEST_HEADERS, 
                                                          TIMEOUT,
                                                          params={"translatedLanguage[]": "en",
                                                                 "order[chapter]": "desc"}).json()["data"]):
            results.add_chapter(
                ChapterNode(detail['id'], f"{detail['attributes']['chapter']} - {detail['attributes']['title']}")
            )

        results.website = self.website_name
        results.website_icon = self.logo
        return results

    async def parse_chapter(self, url):
        chapter = self.load_response(f"{self.api_call_url}/at-home/server/{url}", REQUEST_HEADERS, TIMEOUT).json()["chapter"]

        return ChapterResult(dict(
            enumerate(
                [f"https://uploads.mangadex.org/data/{chapter['hash']}/{filename}" for filename in chapter['data']])
        ))

# Doesn't work right now
# class WattpadExtractor(Extractor):
#     def __init__(self):
#         super().__init__()
#         self.website = '2'
#         self.website_name = 'Wattpad'
#         self.home_page_url = 'https://www.wattpad.com'
#         self.search_page_url = 'https://www.wattpad.com/search/:;'
#         self.logo = 'https://cdn-icons-png.flaticon.com/512/3291/3291661.png'

#     def last_search_page(self, url):
#         # TODO: Haven't figured this one out
#         return 1

#     async def parse_search(self, url):
#         document = self.load_document(self.load_response(url, REQUEST_HEADERS, TIMEOUT))
#         results = dict()

#         if document is not None:
#             for index, search_item in enumerate(document.xpath("//ul[contains(@class, 'list-group')]/li/a")):
#                 result = SearchResult()
#                 result.icon = search_item.xpath(".//div[contains(@class, 'cover')]/img/@src")[0]
#                 result.link = f"{self.home_page_url}{search_item.xpath('@href')[0]}"
#                 result.title = search_item.xpath(".//div[contains(@class, 'title')]")[0].text_content()

#                 for li in search_item.xpath(
#                         ".//div[contains(@class, 'story-info')]/ul[contains(@class, 'story-stats')]/li"):
#                     header = li.xpath("./div[contains(@class, 'label')]/span/text()")[0] + ": "
#                     value = li.xpath(
#                         "./div[contains(@class, 'container')]/div[contains(@class, 'tool-tip')]/span[contains(@class, 'value')]/text()")[
#                         0]
#                     result.add_info(
#                         InfoNode([header, value])
#                     )

#                 results[index] = result

#         return results

#     async def parse_desc(self, url):
#         document = self.load_document(self.load_response(url, REQUEST_HEADERS, TIMEOUT))
#         results = SeriesResult()

#         if document is not None:
#             # Getting stats and tags
#             author = document.xpath("//div[contains(@class, 'author-info')]//text()")[0]

#             for li in document.xpath("//div[contains(@class, 'story-info')]/ul[contains(@class, 'story-stats')]/li"):
#                 header = li.xpath("./div[contains(@class, 'label')]/span/text()")[0] + ": "
#                 value = li.xpath(
#                     "./div[contains(@class, 'container')]/div[contains(@class, 'tool-tip')]/span[contains(@class, 'value')]/text()")[
#                     0]
#                 results.add_info(
#                     InfoNode([header, value])
#                 )

#             results.add_info(InfoNode(["Tags:"]))
#             tags = list()
#             for tag in document.xpath("//div[contains(@class, 'hidden')][./ul]/ul[contains(@class, 'tag-items')]/li"):
#                 tags.append(tag.text_content())
#             results.add_info(InfoNode(tags))

#             # Getting chapters
#             for li in document.xpath("//div[contains(@class, 'story-parts')]/ul/li"):
#                 results.add_chapter(
#                     ChapterNode(f"{self.home_page_url}{li.xpath('./a/@href')[0]}",
#                                 li.xpath(".//div[contains(@class, 'title')]/text()")[0])
#                 )

#             # Getting summary
#             results.summary = ''.join(document.xpath("//pre[contains(@class, 'description')]/text()"))
#             results.title = ''.join(document.xpath("//div[contains(@class, 'story-info__title')]/text()"))
#             results.thumbnail = document.xpath("//div[contains(@class, 'cover')][./img]/img/@src")[0]
#             results.website = self.website_name
#             results.website_icon = self.logo
#         return results

#     async def parse_chapter(self, url):
#         results = dict()
#         page = 1
#         last_page = False

#         while not last_page:
#             document = self.load_document(self.load_response(url + f"/page/{page}", REQUEST_HEADERS, TIMEOUT))
#             if document is not None:
#                 page_container = document.xpath("//div[contains(@class, 'page')]")[0]

#                 results[page] = '\n'.join([p.text_content() for p in page_container.xpath(".//pre/p")])

#                 if not page_container.xpath("contains(@class, 'last-page')"):
#                     page += 1
#                 else:
#                     last_page = True

#         return ChapterResult(pages=results, novel=True)
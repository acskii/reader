"""
Base classes
"""
import requests
from lxml.html import fromstring
from requests import Response 

class Extractor:
    def __init__(self):
        self.website = 0
        self.website_name = ''
        self.home_page_url = ''
        self.search_page_url = ''
        self.logo = ''
        self.key_sep = ':;'
        self.page_sep = ':*'

    def __repr__(self):
        return f"{self.__class__.__name__} <{self.website_name}>"

    @staticmethod
    def load_response(url: str, header: dict, timeout: int, params: dict = {}):
        "Returns a Response from URL"
        response = requests.get(url, headers=header, params=params, timeout=timeout)

        if response is None:
            print(f"NO RESPONSE RECEIVED WHEN LOADING '{url}'")
        else:
            if response.ok:
                return response
            else:
                print(f"RESPONSE NOT OK <Code: {response.status_code}>")
        
        return None

    @staticmethod
    def load_document(response: Response):
        "Returns HTML page from response as a string"
        if response is not None:
            # errors='ignore' used for NON-ASCII characters
            return fromstring(response.content.decode(encoding='utf-8', errors='ignore'))
        else:
            print(f"NO RESPONSE TO LOAD DOCUMENT FROM")
            return None

class InfoNode:
    def __init__(self, info: list = []):
        self.content = info
    
    @property
    def info(self):
        if len(self.content) < 3:
            return ' '.join(self.content)
        else:
            return f"{self.content[0]} {', '.join(self.content[1:])}"

class ChapterNode:
    def __init__(self, chapter_link: str, chapter_header: str):
        self.link = chapter_link
        self.header = chapter_header
    
    @property
    def result(self):
        return (self.header, self.link)
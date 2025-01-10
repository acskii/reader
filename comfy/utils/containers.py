"""
Classes to organise data resulted from extractors.
Extractors are expected to return one of these classes as a result of scraping.
"""

from .base import InfoNode, ChapterNode

class SeriesResult:
    def __init__(self):
        self._info = list()
        self._chapters = list()
        self._title = ''
        self._summary = ''
        self._icon = ''
        self._website = ''
        self._website_logo = ''

    def add_info(self, node: InfoNode):
        self._info.append(node.info)
        
    def add_chapter(self, *args):
        if len(args) >= 1:
            for node in args:
                if type(node) == ChapterNode:
                    self._chapters.append(node)
                else:
                    print(f"Invalid class sent, '{node.__class__.__name__}'")
        else:
            print("No chapter link provided")
                    
    @property
    def chapters(self):
        return self._chapters
        
    @property
    def info(self):
        return self._info

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, text):
        self._summary = text

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, text):
        self._title = text

    @property
    def thumbnail(self):
        return self._icon

    @thumbnail.setter
    def thumbnail(self, link):
        self._icon = link

    @property
    def website(self):
        return self._website

    @website.setter
    def website(self, name: str):
        self._website = name

    @property
    def website_icon(self):
        return self._website_logo

    @website_icon.setter
    def website_icon(self, link):
        self._website_logo = link
    
        
class ChapterResult:
    def __init__(self, pages: dict = {}, novel = False):
        self._pages = pages
        self.novel = novel
        
    @property
    def pages(self):
        return self._pages
        
    def add_page(self, page_content: str):
        last_index = len(self._pages)+1
        self._pages[last_index] = page_content   

class SearchResult:
    def __init__(self, pages: dict = {}):
        self._info = list()
        self._title = ''
        self._icon = ''
        self._link = ''

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, text: str):
        self._title = text

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, img_link: str):
        self._icon = img_link

    @property
    def link(self):
        return self._link

    @link.setter
    def link(self, link: str):
        self._link = link

    @property
    def info(self):
        return self._info

    def add_info(self, node: InfoNode):
        self._info.append(node.info)
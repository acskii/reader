"""
This script acts similarly to an API, where only the needed surface level functions 
are written here. Typically, you need classes.py for this script to work, but you don't need to import classes.py
to use the extractors.

get_extractor(option: int|str) is the main function that will check the availability of a chosen website.
Returns Extractor instance of chosen extractor.
"""

from .classes import *
import re

# WEBSITE OPTION // REGEX
supported_websites = {
    '1': {
        'name': 'bato.to',
        'extractor':  BatoExtractor,
        'url_pattern': r"(?:https?://)?(?:(?:ba|d|h|m|w)to\.to|(?:(?:manga|read)toto|batocomic|[xz]bato)\.(?:com|net|org)|comiko\.(?:net|org)|bat(?:otoo|o?two)\.com)",
    },
    # '2': {
    #     'name': 'wattpad',
    #     'extractor':  WattpadExtractor,
    #     'url_pattern': r"https?://www\.wattpad\.com/story/\w+",
    # },
    '2': {
        'name': 'mangadex',
        'extractor':  MangaDexExtractor,
        'url_pattern': r"(?:https?://)?(?:www\.)?mangadex\.(?:org|cc)",
    },
}

def determine_option(url: str):
    """Get option number based on supported websites, None if not found"""
    for option, info in supported_websites.items():
        if re.match(info['url_pattern'], url.strip()):
            return option

    return None

def get_extractor(website_option: str):
    """Get extractor class of a website according to option number"""
    website_option = str(website_option)

    if website_option in supported_websites:
        return supported_websites[website_option]['extractor']()
    else:
        return None
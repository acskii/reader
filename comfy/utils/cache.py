from django.core.cache import cache
import hashlib, uuid

TIMEOUT = 60 * 30       # 30 minutes

def convert_to_task_id(website_option: str, url: str):
    # Create a MD5 hex string for unique identifier
    hex_string = hashlib.md5(f"{website_option}{url}".encode('utf-8')).hexdigest()
    # Return unique identifier of hex string
    return str(uuid.UUID(hex=hex_string))

async def cached_scrape(func, option: str, **kwargs):
    # Wraps around the normal scrape function, adding the element of caching
    # Needs REDIS server ideally as cache are large in size
    url = kwargs.get('url')
    keywords = kwargs.get('keywords')
    page = kwargs.get('page')

    if (url is not None):
        task_id = convert_to_task_id(option, url)
    elif (keywords is not None) and (page is not None):
        task_id = convert_to_task_id(option, f"{keywords}-page{page}")

    cached = await cache.aget(task_id)

    if cached is not None:
        return cached
    else:
        try:
            if (url is not None):
                result = await func(option, url)
            elif (keywords is not None) and (page is not None):
                result = await func(option, keywords, page)

            if result is not None:
                await cache.aset(task_id, result, timeout=TIMEOUT)
                return result
            else:
                return None
        except TypeError as e:
            print(f"UNEXPECTED ERROR WHEN CACHED SCRAPING: {e}")
            return None

from django.core.cache import cache
import hashlib, uuid

TIMEOUT = 60 * 30       # 30 minutes

def convert_to_task_id(username: str, website_option: str, url: str):
    # Create a MD5 hex string for unique identifier
    hex_string = hashlib.md5(f"{website_option}{url}{username}".encode('utf-8')).hexdigest()
    # Return unique identifier of hex string
    return str(uuid.UUID(hex=hex_string))

async def cached_scape(func, username: str, option: str, url: str):
    # Wraps around the normal scrape function, adding the element of caching
    # Needs REDIS server ideally as cache are large in size
    task_id = convert_to_task_id(username, option, url)

    cached = await cache.aget(task_id)

    if cached is not None:
        return cached
    else:
        try:
            result = await func(option, url)
            
            if result is not None:
                await cache.aset(task_id, result, timeout=TIMEOUT)
                return result
            else:
                return None
        except TypeError as e:
            print(f"UNEXPECTED ERROR WHEN CACHED SCRAPING: {e}")
            return None

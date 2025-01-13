from ..extractors.extract import get_extractor

async def scrape_info(website_option: str, url: str):
    extractor = get_extractor(website_option)
    
    if extractor is not None:
        results = await extractor.parse_desc(url)
        
        if results is not None: return results

    return None

async def scrape_results(website_option: str, keywords: str, page: int):
    extractor = get_extractor(website_option)
    
    if extractor is not None:
        results = await extractor.parse_search(keywords, page)
        
        if results is not None: return results

    return None

async def scrape_chapter(website_option: str, url: str):
    extractor = get_extractor(website_option)
    
    if extractor is not None:
        results = await extractor.parse_chapter(url)
        if results is not None: return results

    return None
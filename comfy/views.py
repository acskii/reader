from django.shortcuts import render, redirect, reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.core.cache import cache
from comfy.models import VisitHistory
from asgiref.sync import sync_to_async
import datetime
from .extractors.extract import determine_option, get_supported_websites
from .utils.scrape import scrape_info, scrape_chapter, scrape_results
from .utils.cache import cached_scrape

ERR_URL_WRONG = "URL entered is not recognised"
CACHE_TIMEOUT = 60 * 60             # 1 hour cache

@sync_to_async
def get_user_name(request):
    return request.user.get_username()

def register_view(request):
    if request.user.is_authenticated:
        return redirect(reverse('comfy:home'))
    else:
        if request.method == 'POST':
            form = UserCreationForm(request.POST)

            if form.is_valid():
                login(request, form.save())
                return redirect(reverse('comfy:home'))
        else:
            form = UserCreationForm()

        return render(request, 'registration/sign_up.html', {'form': form})

@login_required
async def home_view(request):
    if request.method == 'POST':
        # User entered a URL in the snatch form
        if 'home-extract-form' in request.POST:
            
            typed_url = request.POST.get('url', None)
            if typed_url is not None:
                option = determine_option(typed_url)
                username = await get_user_name(request)
                            
                if option is not None:
                    await cache.aset(f'{username}-option', option, timeout=CACHE_TIMEOUT)
                    await cache.aset(f'{username}-series_url', typed_url.strip(), timeout=CACHE_TIMEOUT)
                    return redirect(reverse('comfy:series'))
            return render(request, 'home/home.html', {'error': ERR_URL_WRONG})
        
        elif 'visit-series' in request.POST:
            last_visited = await sync_to_async(VisitHistory.objects.all)()
            series_url = request.POST.get('visit-series', None)
            username = await get_user_name(request)

            if series_url is not None:
                async for visit in last_visited:
                    if visit.series_url == series_url:
                        await cache.aset(f'{username}-option', visit.website_option, timeout=CACHE_TIMEOUT)
                        await cache.aset(f'{username}-series_url', series_url, timeout=CACHE_TIMEOUT)

                        return redirect(reverse('comfy:series'))
                    
            # error page        
            return redirect(reverse('comfy:home'))

        elif 'visit-preview' in request.POST:
            last_visited = await sync_to_async(VisitHistory.objects.all)()
            preview_url = request.POST.get('visit-preview', None)
            username = await get_user_name(request)
            option = await cache.aget(f'{username}-option')

            if preview_url is not None:
                async for visit in last_visited:
                    if visit.preview_url == preview_url:
                        results = await cached_scrape(scrape_info, visit.website_option, url=visit.series_url)
                        print(visit.title)
                        if results is not None:
                            new_chapter_list = results.chapters
                            print(new_chapter_list)
                            await cache.aset(f'{username}-option', visit.website_option, timeout=CACHE_TIMEOUT)
                            await cache.aset(f'{username}-preview_url', preview_url, timeout=CACHE_TIMEOUT)
                            await cache.aset(f'{username}-series_url', visit.series_url, timeout=CACHE_TIMEOUT)
                            await cache.aset(f'{username}-current_chapter_list', new_chapter_list, timeout=CACHE_TIMEOUT)
                            return redirect(reverse('comfy:preview'))  

            # error page        
            return redirect(reverse('comfy:home'))
    else:
        # Gets series that were last visited
        last_visited = VisitHistory.objects.all().order_by('-last_visited')
        return await sync_to_async(render)(request, 'home/home.html', {'visited': last_visited,
                                                                       'supported': get_supported_websites()})
@login_required
async def snatch_view(request):
    if request.method == 'POST':
        typed_url = request.POST.get('url', None)
        if typed_url is not None:
            option = determine_option(typed_url)
            username = await get_user_name(request)
                        
            if option is not None:
                await cache.aset(f'{username}-option', option, timeout=CACHE_TIMEOUT)
                await cache.aset(f'{username}-series_url', typed_url.strip(), timeout=CACHE_TIMEOUT)
                return redirect(reverse('comfy:series'))
        return await sync_to_async(render)(request, 'snatch/snatch.html', {'error': ERR_URL_WRONG})
    else:
        return await sync_to_async(render)(request, 'snatch/snatch.html', {'supported': get_supported_websites()})

@login_required
async def search_view(request):
    if request.method == 'POST':
        if ('website' in request.POST) and ('keywords' in request.POST):
            # Do searching
            username = await get_user_name(request)
            option = request.POST.get('website')
            keywords = request.POST.get('keywords')

            # Get search results
            # Cache results for faster retrieval
            await cache.aset(f'{username}-soption', option, timeout=CACHE_TIMEOUT)
            results = await cached_scrape(scrape_results, option, keywords=keywords, page=1)
            # Render results

            if results is not None:
                print(results)
                return await sync_to_async(render)(request, 'search/results.html', {'website_options': get_supported_websites(),
                                                                                    'keywords': keywords,
                                                                                    'website': option,
                                                                                    'search_results': results})
            else:
                return await sync_to_async(render)(request, 'search/results.html', {'website_options': get_supported_websites(),
                                                                                    'keywords': keywords,
                                                                                    'website': option})
        elif 'extract-result' in request.POST:
            username = await get_user_name(request)
            option = await cache.aget(f'{username}-soption')
            series_url = request.POST.get('extract-result')

            # Cache results
            await cache.aset(f'{username}-option', option, timeout=CACHE_TIMEOUT)
            await cache.aset(f'{username}-series_url', series_url, timeout=CACHE_TIMEOUT)

            # Redirect
            return redirect(reverse('comfy:series'))
        
        return await sync_to_async(render)(request, 'search/search.html', {'website_options': get_supported_websites()})
    else:
        return await sync_to_async(render)(request, 'search/search.html', {'website_options': get_supported_websites()})

@login_required
async def extract_view(request):
    if request.method == 'GET':
        username = await get_user_name(request)
        option = await cache.aget(f'{username}-option')
        url = await cache.aget(f'{username}-series_url')

        print(option, url)
        if (option is not None) and (url is not None):
            results = await cached_scrape(scrape_info, option, url=url)

            if results is not None:
                # Cache chapter list for future preview use
                chapters = results.chapters
                await cache.aset(f'{username}-current_chapter_list', chapters, timeout=CACHE_TIMEOUT)

                # Save series as last visited
                query = VisitHistory.objects.filter(user=request.user, series_url=url)
                if await sync_to_async(query.first)() is None:
                    series_visit = VisitHistory(user=request.user, 
                                                title=results.title,
                                                series_url=url,
                                                website_option=option,
                                                logo=results.thumbnail)
                else:
                    series_visit = await sync_to_async(query.first)()
                    series_visit.last_visited = datetime.datetime.now()
                
                await sync_to_async(series_visit.save)()
                # return rendered template
                return await sync_to_async(render)(request, 'series/series.html', {'results': results})
        
        # redirect to error page soon
        return redirect(reverse('comfy:home'))
    else:
        # A chapter was selected for preview
        username = await get_user_name(request)
        url = request.POST.get('preview_url', None)

        if url is not None:
            # Cache url for preview page
            await cache.aset(f'{username}-preview_url', url, timeout=CACHE_TIMEOUT)

            # Save chapter in last visited history
            chapters = await cache.aget(f'{username}-current_chapter_list')
            query = await sync_to_async(VisitHistory.objects.filter)(user=request.user, series_url=url)
            series_visit = await sync_to_async(query.first)()

            if series_visit is not None:
                for chapter in chapters:
                    if chapter.link == url:
                        series_visit.last_read = chapter.header

                series_visit.preview_url = url
                await sync_to_async(series_visit.save)()
    
            return redirect(reverse('comfy:preview'))

@login_required
async def preview_view(request):
    if request.method == 'POST':
        url = request.POST.get('nav_url', None)
        username = await get_user_name(request)

        if url is not None:
            await cache.aset(f'{username}-preview_url', url, timeout=CACHE_TIMEOUT)

            # Save chapter in last visited history
            chapters = await cache.aget(f'{username}-current_chapter_list')
            query = await sync_to_async(VisitHistory.objects.filter)(user=request.user, series_url=url)
            series_visit = await sync_to_async(query.first)()

            if series_visit is not None:
                for chapter in chapters:
                    if chapter.link == url:
                        series_visit.last_read = chapter.header

                series_visit.preview_url = url
                series_visit.last_visited = datetime.datetime.now()
                await sync_to_async(series_visit.save)()

            return redirect(reverse('comfy:preview'))
    else:
        # Getting information from cache
        username = await get_user_name(request)
        option = await cache.aget(f'{username}-option')
        url = await cache.aget(f'{username}-preview_url')
        chapter_list = await cache.aget(f'{username}-current_chapter_list')

        if (option is not None) and (url is not None) and (chapter_list is not None):
            results = await cached_scrape(scrape_chapter, option, url=url)
            if results is not None:
                # Getting navigation urls
                prev_link, next_link = None, None

                for index, chapter in enumerate(chapter_list):
                    if chapter.link == url:
                        if index > 0:
                            prev_link = chapter_list[index-1].link
                        
                        if index < len(chapter_list)-1:
                            next_link = chapter_list[index+1].link

                # Save chapter in last visited history
                series_url = await cache.aget(f'{username}-series_url')
                query = await sync_to_async(VisitHistory.objects.filter)(user=request.user, series_url=series_url)
                series_visit = await sync_to_async(query.first)()

                if series_visit is not None:
                    for chapter in chapter_list:
                        if chapter.link == url:
                            series_visit.last_read = chapter.header

                series_visit.preview_url = url
                series_visit.last_visited = datetime.datetime.now()
                await sync_to_async(series_visit.save)()

                return await sync_to_async(render)(request, 'preview/preview.html', {
                    'content': results,
                    'chapters': chapter_list,
                    'current_chapter_url': url,
                    'previous_url': prev_link,
                    'next_url': next_link
                })

    # error page redirect here
    return redirect(reverse('comfy:home'))

@login_required
def logout_direct(request):
    if request.method == 'POST':
        logout(request)
    return redirect(reverse('comfy:login'))

from django.shortcuts import render, redirect, reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.core.cache import cache
from asgiref.sync import sync_to_async
from .extractors.extract import determine_option
from .utils.scrape import scrape_info
from .utils.cache import cached_scape

ERR_URL_WRONG = "URL entered is not recognised"
CACHE_TIMEOUT = 60 * 60             # 1 hour cache

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

        return render(request, 'registration/sign_up.html', {"form": form})

@login_required
def home_view(request):
    if request.method == 'POST':
        # User entered a URL in the snatch form
        if 'home-extract-form' in request.POST:
            
            typed_url = request.POST.get('url', None)
            if typed_url is not None:
                option = determine_option(typed_url)

                if option is not None:
                    cache.set('option', option, timeout=CACHE_TIMEOUT)
                    cache.set('series_url', typed_url.strip(), timeout=CACHE_TIMEOUT)
                    return redirect(reverse('comfy:series'))
            return render(request, 'home/home.html', {"error": ERR_URL_WRONG})
        
    return render(request, 'home/home.html')

@sync_to_async
def get_username(request):
    return request.user.get_username()

@login_required
async def extract_view(request):
    if request.method == 'GET':
        option = await cache.aget('option')
        url = await cache.aget('series_url')

        if (option is not None) and (url is not None):
            username = await get_username(request)
            results = await cached_scape(scrape_info, username, option, url)

            if results is not None:
                # Cache chapter list for future preview use
                chapters = results.chapters

                await cache.aset('current_chapter_list', chapters, timeout=CACHE_TIMEOUT)

                # return rendered template
                return await sync_to_async(render)(request, 'series/series.html', {'results': results})
        
        # redirect to error page soon
        return redirect(reverse('comfy:home'))
    else:
        # A chapter was selected for preview
        url = request.POST.get('preview_url', None)

        if url is not None:
            await cache.aset('preview_url', url, timeout=CACHE_TIMEOUT)
            return redirect(reverse('comfy:preview'))

@login_required
def logout_direct(request):
    if request.method == 'POST':
        logout(request)
    return redirect(reverse('comfy:login'))

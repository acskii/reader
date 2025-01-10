from django.shortcuts import render, redirect, reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.core.cache import cache
from .extractors.extract import determine_option
from .utils.cache import cached_scrape

ERR_URL_WRONG = "URL entered is not recognised"

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
                    cache.set('option', option, timeout=3600)
                    cache.set('series_url', typed_url.strip(), timeout=3600)
                    return redirect(reverse('comfy:series'))
            return render(request, 'home/home.html', {"error": ERR_URL_WRONG})
        
    return render(request, 'home/home.html')

@login_required
async def extract_view(request):
    pass

@login_required
def logout_direct(request):
    if request.method == 'POST':
        logout(request)
    return redirect(reverse('comfy:login'))

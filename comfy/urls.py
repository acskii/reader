from django.urls import path
from . import views

app_name = 'comfy'
urlpatterns = [
    path('', views.home_view, name='home_index'),
    path('home/', views.home_view, name='home'),
    path('signup/', views.register_view, name='signup'),
]
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'comfy'
urlpatterns = [
    path('', views.home_view, name='home_index'),
    path('home/', views.home_view, name='home'),
    path('series/', views.extract_view, name='series'),
    path('signup/', views.register_view, name='signup'),
    path('logout/', views.logout_direct, name='logout'),
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
]
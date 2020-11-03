from django.urls import path
from . import views

urlpatterns = [
    path('search_posts', views.search, name='search_posts')
]
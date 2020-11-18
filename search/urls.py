from django.urls import path
from . import views

urlpatterns = [
    path('search_chats/', views.search_chats, name='search_chats'),
    path('search_photoalbums/', views.search_photoalbums, name='search_photoalbums'),
    path('search_images/', views.search_images, name='search_images'),
    path('search_users/', views.search_users, name='search_users'),
    path('search_everything/', views.search_everything, name='search_everything')
]

from django.urls import path

from . import views

urlpatterns = [
    path('block_user/<int:pk>/', views.block_user, name='block_user'),
    path('unblock_user/<int:pk>/', views.unblock_user, name='unblock_user'),
    path('blocked_users/', views.blocked_users, name='blocked_users'),
]
from django.urls import path

from . import views

urlpatterns = [
    path('friends/<int:pk>/', views.friends, name='friends'),
    path('friend_request/send/<int:pk>/', views.send_friend_request, name='send_friend_request'),
    path('friend_request/cancel/<int:pk>/', views.cancel_friend_request, name='cancel_friend_request'),
    path('friend_request/accept/<int:pk>/', views.accept_friend_request, name='accept_friend_request'),
    path('friend_request/delete/<int:pk>/', views.delete_friend_request, name='delete_friend_request'),
    path('friend_request/remove/<int:pk>/', views.remove_friend, name='remove_friend'),
]
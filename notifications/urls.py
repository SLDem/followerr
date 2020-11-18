from django.urls import path
from . import views

urlpatterns = [
    path('view_notifications/', views.view_notifications, name='view_notifications'),
    path('clear_all_notifications/', views.clear_all_notifications, name='clear_all_notifications'),
    path('clear_post_notifications/', views.clear_post_notifications, name='clear_post_notifications'),
    path('clear_message_notifications/', views.clear_message_notifications, name='clear_message_notifications'),
    path('clear_friend_request_notifications/', views.clear_friend_request_notifications, name='clear_friend_request_notifications'),
]

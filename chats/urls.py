from django.urls import path
from . import views

urlpatterns = [
    path("messages/", views.messages, name='messages'),
    path("delete_message/<int:pk>/", views.delete_message, name='delete_message'),
    path("chat/<int:pk>/", views.chat, name='chat'),
    path("edit_chat/<int:pk>/", views.edit_chat, name='edit_chat'),
    path("delete_chat/<int:pk>/", views.delete_chat, name='delete_chat'),
    path("add_users_to_chat/<int:pk>/", views.add_users_to_chat, name='add_users_to_chat'),
    path("chat_users/<int:pk>/", views.chat_users, name='chat_users'),
    path("remove_user_from_chat/<int:pk>/<int:user_pk>/", views.remove_user_from_chat, name='remove_user_from_chat'),
    path("leave_chat/<int:pk>/", views.leave_chat, name='leave_chat'),
    path('create_private_chat/<int:pk>/', views.create_private_chat, name='create_private_chat')
]
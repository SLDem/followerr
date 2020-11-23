from django.urls import path
from django.contrib.auth. decorators import login_required

from . import views

urlpatterns = [
    path('profile/<int:pk>/', login_required(views.profile), name='profile'),
    path('edit_user/<int:pk>/', views.edit_user, name='edit_user'),
    path('change_password/', views.change_password, name='change_password'),
    path('upload_avatar/', views.upload_avatar, name='upload_avatar'),
    path('subscribe_to_user/<int:pk>/', views.subscribe_to_user, name='subscribe_to_user'),
    path('unsubscribe_from_user/<int:pk>', views.unsubscribe_from_user, name='unsubscribe_from_user'),

    path('usersAPI/', views.UsersView.as_view()),
]
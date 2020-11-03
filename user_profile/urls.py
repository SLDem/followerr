from django.urls import path
from django.contrib.auth. decorators import login_required

from . import views

urlpatterns = [
    path('profile/<int:pk>/', login_required(views.profile), name='profile'),
    path('edit_user/<int:pk>/', views.edit_user, name='edit_user'),
    path('change_password/', views.change_password, name='change_password'),
    path('upload_avatar/', views.upload_avatar, name='upload_avatar'),
    path('all_users_list/', views.all_users_list, name='all_users_list'),
]
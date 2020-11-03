from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.index, name='index'),
    path('', views.index, name='index'),
    path('delete_post/<int:pk>/', views.delete_post, name='delete_post'),
    path('edit_post/<int:pk>/', views.edit_post, name='edit_post'),
    path('post_detail/<int:pk>', views.post_detail, name='post_detail'),
    path("dislike_post/<int:pk>/", views.dislike_post, name="dislike_post"),
    path("like_post/<int:pk>/", views.like_post, name="like_post"),
]
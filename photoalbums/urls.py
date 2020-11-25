from django.urls import path
from . import views

urlpatterns = [
    path('photoalbums/<int:pk>/', views.photoalbums, name='photoalbums'),
    path('photoalbum/<int:pk>/', views.photoalbum, name='photoalbum'),
    path('image-detail/<int:pk>/', views.image_detail, name='image-detail'),
    path('reply-form_picture/<int:pk>/<int:parent_id>/', views.reply_form_picture, name='reply_form_picture'),
    path('make_avatar/<int:pk>/', views.make_avatar, name='make_avatar'),
    path('edit_image/<int:pk>/', views.edit_image, name='edit_image'),
    path('delete_image/<int:pk>/', views.delete_image, name='delete_image'),
    path('edit_album/<int:pk>/', views.edit_album, name='edit_album'),
    path('delete_album/<int:pk>/', views.delete_album, name='delete_album'),
    path('like_image/<int:pk>/', views.like_image, name='like_image'),
    path('dislike_image/<int:pk>/', views.dislike_image, name='dislike_image'),
]
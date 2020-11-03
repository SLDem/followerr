from django.urls import path
from . import views

urlpatterns = [
    path('delete_comment/<int:pk>/', views.delete_comment, name='delete_comment'),
    path('edit_comment/<int:pk>/', views.edit_comment, name='edit_comment'),
    path("like_comment/<int:pk>/", views.like_comment, name="like_comment"),
    path("dislike_comment/<int:pk>/", views.dislike_comment, name="dislike_comment"),
    path("reply_form/<int:pk>/<int:parent_id>/", views.reply_form, name="reply_form"),
]
from django.urls import path
from . import views

urlpatterns = [
    path("groups/<int:pk>/", views.groups, name='groups'),
    path("group_detail/<int:pk>/", views.group_detail, name='group_detail'),
    path("discussions_list/<int:pk>/", views.discussions_list, name='discussions_list'),
    path("discussion/<int:pk>/", views.discussion, name='discussion'),
    path("remove_discussion/<int:pk>/", views.remove_discussion, name='remove_discussion'),
    path("join_or_leave_group/<int:pk>/", views.join_or_leave_group, name='join_or_leave_group'),
    path("group_request/send/<int:pk>/", views.send_group_request, name='send_group_request'),
    path("group_request/cancel/<int:pk>/", views.cancel_group_request, name='cancel_group_request'),
    path("group_request/accept/<int:pk>/<int:user_pk>/", views.accept_group_request, name='accept_group_request'),
    path("group_request/delete/<int:pk>/<int:user_pk>/", views.delete_group_request, name='delete_group_request'),
    path("group_management/<int:pk>/", views.group_management, name='group_management'),
    path("group_users/<int:pk>/", views.group_users, name='group_users'),
    path("remove_user_from_group/<int:pk>/<int:user_pk>/", views.remove_user_from_group, name='remove_user_from_group'),
    path("delete_group/<int:pk>/", views.delete_group, name='delete_group'),
    path("make_owner/<int:pk>/<int:user_pk>/", views.make_owner, name='make_owner'),
    path("remove_owner/<int:pk>/<int:user_pk>/", views.remove_owner, name='remove_owner'),
]
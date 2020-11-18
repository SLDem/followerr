from django.shortcuts import render, HttpResponse, redirect

from user_profile.models import User
from .models import Notification


def view_notifications(request):
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'notifications/notifications.html', {'notifications': notifications, 'title': 'Notifications'})


def clear_all_notifications(request):
    notifications = Notification.objects.filter(user=request.user)
    for n in notifications:
        n.delete()
    return redirect('view_notifications')


def clear_post_notifications(request):
    notifications = Notification.objects.filter(user=request.user, post__isnull=False)
    for n in notifications:
        n.delete()
    return redirect('view_notifications')


def clear_message_notifications(request):
    notifications = Notification.objects.filter(user=request.user, post__isnull=False)
    for n in notifications:
        n.delete()
    return redirect('view_notifications')


def clear_friend_request_notifications(request):
    notifications = Notification.objects.filter(user=request.user, friend_request__isnull=False)
    for n in notifications:
        n.delete()
    return redirect('view_notifications')


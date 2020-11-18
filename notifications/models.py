from django.db import models

from user_profile.models import User
from posts.models import Post
from chats.models import Message
from friends.models import FriendRequest


class Notification(models.Model):
    objects: models.Manager()

    P = 'P'
    M = 'M'
    FR = 'FR'

    NOTIFICATION_CHOICES = [
        (P, 'P'),
        (M, 'M'),
        (FR, 'FR'),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True)
    friend_request = models.ForeignKey(FriendRequest, on_delete=models.CASCADE, null=True, blank=True)

    type = models.CharField(choices=NOTIFICATION_CHOICES, max_length=200)
    text = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_notifications')
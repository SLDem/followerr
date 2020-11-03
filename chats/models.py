from django.db import models
from user_profile.models import User
from groups.models import Discussion


class Chat(models.Model):
    objects: models.Manager()

    image = models.ImageField('Add group avatar', upload_to='group_avatars', null=True, blank=True)
    title = models.TextField('Title', max_length=250)

    owner = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='owner', null=True)
    users = models.ManyToManyField(User, related_name='chat_users')


class Message(models.Model):
    objects: models.Manager()

    image = models.ImageField('Attach an image', upload_to='images', null=True, blank=True)
    body = models.CharField('Body', max_length=10000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    from_user = models.ForeignKey(User, related_name='message_from_user', on_delete=models.PROTECT, null=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='message_chat', null=True)
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='message_discussion', null=True)


class PrivateMessage(models.Model):
    objects: models.Manager()

    image = models.ImageField('Attach an image', upload_to='images', null=True, blank=True)
    body = models.CharField('Body', max_length=10000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    from_user = models.ForeignKey(User, related_name='private_message_from_user', on_delete=models.SET_NULL, null=True)
    to_user = models.ForeignKey(User, related_name='private_message_to_user', on_delete=models.SET_NULL, null=True)

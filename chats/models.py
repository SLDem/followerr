from django.db import models
from user_profile.models import User
from groups.models import Discussion


class Chat(models.Model):
    objects: models.Manager()

    image = models.ImageField('Add chat avatar', upload_to='group_avatars', null=True, blank=True)
    title = models.TextField('Title', max_length=250)
    unread_count = models.IntegerField(default=0)
    is_private = models.BooleanField(default=False)

    owner = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='owner', null=True)
    users = models.ManyToManyField(User, related_name='chat_users')
    last_message = models.ForeignKey("Message", related_name='last_chat_message', null=True, blank=True,
                                     on_delete=models.SET_NULL)


class Message(models.Model):
    objects: models.Manager()

    image = models.ImageField('Attach an image', upload_to='images', null=True, blank=True)
    body = models.CharField('Body', max_length=10000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_read = models.BooleanField(default=False)

    from_user = models.ForeignKey(User, related_name='message_from_user', on_delete=models.PROTECT, null=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='chat_messages', null=True)
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='message_discussion', null=True, blank=True)

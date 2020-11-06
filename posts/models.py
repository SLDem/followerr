from django.db import models
from user_profile.models import User
from groups.models import Group
from django.utils import timezone
import datetime


class Post(models.Model):
    objects: models.Manager()

    body = models.TextField('Body', max_length=2000)
    image = models.ImageField('Attach an image', upload_to='images', null=True, blank=True)
    date_posted = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='author', null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_post', null=True, blank=True)
    likers = models.ManyToManyField(User, related_name='likers', blank=True)
    dislikers = models.ManyToManyField(User, related_name='dislikers', blank=True)

    def __unicode__(self):
        return self.body

    def get_absolute_url(self):
        return "/post_detail/%i/" % self.pk


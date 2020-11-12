from django.db import models
from user_profile.models import User


class Photoalbum(models.Model):
    objects: models.Manager()

    title = models.TextField("Title", max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='album_owner', null=False, blank=False)


class Image(models.Model):
    objects: models.Manager()

    image = models.ImageField('Image', upload_to='images', null=False, blank=False)
    description = models.TextField('Description', max_length=4000, null=True, blank=True)

    album = models.ForeignKey('Photoalbum', related_name='album_images', null=False, on_delete=models.CASCADE)
    likers = models.ManyToManyField(User, related_name='image_likers', blank=True)
    dislikers = models.ManyToManyField(User, related_name='image_dislikers', blank=True)
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from user_profile.models import User
from posts.models import Post
from photoalbums.models import Image


class Comment(MPTTModel):
    objects: models.Manager()

    body = models.TextField(max_length=1000)
    date_posted = models.DateTimeField(auto_now_add=True)

    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='comment_author')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comments', null=True, blank=True)
    picture = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='picture_comments', null=True, blank=True)
    likers = models.ManyToManyField(User, related_name='comment_likers', blank=True)
    dislikers = models.ManyToManyField(User, related_name='comment_dislikers', blank=True)

    class MPTTMeta:
        order_insertion_by = ['date_posted']

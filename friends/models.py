from django.db import models
from user_profile.models import User


class FriendRequest(models.Model):
    objects: models.Manager()

    to_user = models.ForeignKey(User, related_name='to_user', on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, related_name='from_user', on_delete=models.CASCADE)
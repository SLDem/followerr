from django.db import models
from user_profile.models import User


class Group(models.Model):
    objects: models.Manager()

    title = models.CharField('Title', max_length=100, null=False, blank=False)
    description = models.CharField('Description', max_length=4000, null=True, blank=True)
    group_avatar = models.ImageField('Group Avatar', upload_to='group_avatars', blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField('Is this a private group?', default=False)

    users = models.ManyToManyField(User, related_name='group_members')
    owners = models.ManyToManyField(User, related_name='group_owners')
    admin = models.ForeignKey(User, related_name='group_admin', on_delete=models.CASCADE, null=True)


class GroupJoinRequest(models.Model):
    objects: models.Manager()

    to_group = models.ForeignKey(Group, related_name='to_group', on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, related_name='from_user_to_group', on_delete=models.CASCADE)


class Discussion(models.Model):
    objects: models.Manager()

    title = models.CharField('Title', max_length=200)
    description = models.CharField('Description', max_length=200)

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='discussion_author')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='discussion_group')

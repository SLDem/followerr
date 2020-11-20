from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from user_profile.models import User
from groups.models import Group
from friends.models import FriendRequest
from groups.models import GroupJoinRequest, Discussion
from posts.models import Post
from comments.models import Comment
from chats.models import Message, Chat
from photoalbums.models import Image, Photoalbum
from notifications.models import Notification


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password', 'name', 'last_login')}),
        ('Permissions', {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
            'user_permissions',
            'friends',
            'blocked_users',
            'image',
            'gender',
            'subscribers',
            'messages_to_resend'
        )}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2')
            }
        ),
    )

    list_display = ('email', 'name', 'is_staff', 'last_login', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('user_permissions',)


class PostsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'body', 'image', 'date_posted')
    list_filter = ('body', )



class NotificationAdmin(admin.ModelAdmin):
    list_display = ('pk', 'post', 'message', 'friend_request', 'type', 'text', 'user')


admin.site.register(User, UserAdmin)

admin.site.register(Group)

admin.site.register(FriendRequest)

admin.site.register(GroupJoinRequest)

admin.site.register(Post, PostsAdmin)

admin.site.register(Comment)

admin.site.register(Message)

admin.site.register(Chat)
admin.site.register(Discussion)

admin.site.register(Photoalbum)
admin.site.register(Image)

admin.site.register(Notification, NotificationAdmin)

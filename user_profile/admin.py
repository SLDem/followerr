from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from user_profile.models import User
from groups.models import Group
from friends.models import FriendRequest
from groups.models import GroupJoinRequest, Discussion
from posts.models import Post
from comments.models import Comment
from chats.models import Message, PrivateMessage, Chat
from photoalbums.models import Image, Photoalbum


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password', 'name', 'last_login')}),
        ('Permissions', {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
            'user_permissions',
            'blocked_users',
            'avatar',
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


admin.site.register(User, UserAdmin)

admin.site.register(Group)

admin.site.register(FriendRequest)

admin.site.register(GroupJoinRequest)

admin.site.register(Post)

admin.site.register(Comment)

admin.site.register(Message)

admin.site.register(PrivateMessage)
admin.site.register(Chat)
admin.site.register(Discussion)

admin.site.register(Photoalbum)
admin.site.register(Image)

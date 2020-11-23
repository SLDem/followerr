from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'name', 'city', 'gender', 'following', 'last_online', 'is_staff', 'is_superuser',
                  'is_active', 'date_joined', 'about_me', 'favourite_music', 'favourite_books', 'favourite_movies',
                  'friends', 'blocked_users', 'subscribers', 'image')

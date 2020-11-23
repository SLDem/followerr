from rest_framework import serializers
from .models import Post
from user_profile.serializers import UserSerializer


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('body', 'image', 'date_posted', 'is_private', 'user', 'group', 'profile', 'likers', 'dislikers')


    def create(self, validated_data):
        return Post.objects.create(**validated_data)

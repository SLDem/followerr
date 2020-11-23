from django.shortcuts import render, redirect
from django.http import HttpResponse
from comments.forms import NewCommentForm
from django.core.paginator import Paginator

from .forms import NewPostForm

from .models import Post
from groups.models import Group
from comments.models import Comment
from notifications.models import Notification

from authentication.views import see_online_users

from search.documents import PostDocument

from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import PostSerializer


def index(request):
    title = 'Home'
    online_users = see_online_users()
    user_groups = Group.objects.filter(users__id=request.user.pk)

    def search_posts(request):
        q = request.GET.get('q')

        if q:
            searched_posts = PostDocument.search().query('match', body=q)
        else:
            searched_posts = ''
        return searched_posts

    searched_posts = search_posts(request)

    if request.user.is_authenticated:
        user = request.user
        user_posts = Post.objects.filter(user=request.user).exclude(is_private=True)
        friends_posts = Post.objects.filter(user__in=user.friends.all()).exclude(is_private=True)
        user_group_posts = Post.objects.filter(group__in=user_groups).exclude(is_private=True)

        posts = friends_posts.union(user_posts, user_group_posts)[::-1]
        posts_paginator = Paginator(posts, 5)
        page_obj = posts_paginator.get_page(request.GET.get('page'))

        if request.method == 'POST':
            form = NewPostForm(request.POST, request.FILES)
            if form.is_valid():
                new_post = form.save(commit=False)
                new_post.user = user
                new_post.save()
                for user in request.user.subscribers.all():
                    notification = Notification.objects.create(type='P', text='New Post in subscribed!', user=user, post=new_post)
                    notification.save()
                return redirect('index')
        else:
            form = NewPostForm(instance=None)

        context = {
            'form': form,
            'posts': posts,
            'searched_posts': searched_posts,
            'online_users': online_users,
            'page_obj': page_obj,
            'title': title,
        }

        return render(request, 'posts/index.html', context=context)
    else:
        return redirect('login')


class IndexView(APIView):
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response({'posts': serializer.data})

    def post(self, request):
        post = request.data.get('post')
        serializer = PostSerializer(data=post)
        if serializer.is_valid(raise_exception=True):
            post_saved = serializer.save()
        return Response({'success': 'Post {} created successfully'.format(post_saved.pk)})


def post_detail(request, pk):
    try:
        title = 'Post Comments'
        online_users = see_online_users()
        post = Post.objects.get(pk=pk)
        if request.user.is_authenticated:
            comments = Comment.objects.filter(post=post)
            if request.method == 'POST':
                form = NewCommentForm(request.POST)
                if form.is_valid():
                    new_comment = form.save(commit=False)
                    new_comment.user = request.user
                    new_comment.parent_id = request.POST.get("parent_id")
                    new_comment.post = post
                    new_comment.save()
                    return redirect('post_detail', pk=post.pk)
            else:
                form = NewCommentForm(instance=None)
            return render(request, 'posts/post_detail.html', {'form': form,
                                                              'post': post,
                                                              'online_users': online_users,
                                                              'comments': comments,
                                                              'title': title})
        else:
            return redirect('login')
    except Exception as ex:
        pass
    return HttpResponse('Post does not exist')


def edit_post(request, pk):
    try:
        post = Post.objects.get(pk=pk)
        title = 'Edit Post'
        if request.user.is_authenticated:
            if request.user == post.user:
                if request.method == 'POST':
                    form = NewPostForm(request.POST, request.FILES, instance=post)
                    if form.is_valid():
                        form.save()
                        return redirect('post_detail', pk=post.pk)
                else:
                    form = NewPostForm(instance=post)
            else:
                return HttpResponse('Action not allowed')
        else:
            return redirect('login')
        form = NewPostForm(instance=post)
        return render(request, 'posts/edit_post.html', {'form': form,
                                                        'post': post,
                                                        'title': title})
    except Exception as ex:
        return HttpResponse(ex)


def like_post(request, pk):
    try:
        user = request.user
        post = Post.objects.get(pk=pk)
        if user in post.likers.all():
            post.likers.remove(user)
            post.save()
            return redirect(request.META.get('HTTP_REFERER'))
        elif user not in post.likers.all() and user in post.dislikers.all():
            post.likers.add(user)
            post.dislikers.remove(user)
            post.save()
        else:
            post.likers.add(user)
            post.save()
        return redirect(request.META.get('HTTP_REFERER'))
    except Exception:
        pass
    return HttpResponse('Post does not exist')


def dislike_post(request, pk):
    try:
        user = request.user
        post = Post.objects.get(pk=pk)
        if request.user in post.dislikers.all():
            post.dislikers.remove(user)
            post.save()
            return redirect(request.META.get('HTTP_REFERER'))
        elif user not in post.dislikers.all() and user in post.likers.all():
            post.dislikers.add(user)
            post.likers.remove(user)
            post.save()
        else:
            post.dislikers.add(user)
            post.save()
        return redirect(request.META.get('HTTP_REFERER'))
    except Exception:
        pass
    return HttpResponse('Post does not exist')


def delete_post(request, pk):
    try:
        post = Post.objects.get(pk=pk)
        if post.user == request.user or post.profile == request.user:
            post.delete()
            return redirect('index')
        else:
            return HttpResponse('You can only delete your own posts')
    except Exception:
        pass
    return HttpResponse('Post does not exist')
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import NewPostForm
from comments.forms import NewCommentForm
from django.core.paginator import Paginator

from .models import Post
from groups.models import Group
from comments.models import Comment
from authentication.views import see_online_users


def index(request):
    online_users = see_online_users()
    user_groups = Group.objects.filter(users__id=request.user.pk)

    if request.user.is_authenticated:
        user = request.user
        friends_posts = Post.objects.filter(user__in=user.friends.all())
        user_posts = Post.objects.filter(user=request.user)
        user_group_posts = Post.objects.filter(group__in=user_groups)

        posts = friends_posts.union(user_posts, user_group_posts)[::-1]
        posts_paginator = Paginator(posts, 5)
        page_number = request.GET.get('page')
        page_obj = posts_paginator.get_page(page_number)

        if request.method == 'POST':
            form = NewPostForm(request.POST, request.FILES)
            if form.is_valid():
                new_post = form.save(commit=False)
                new_post.user = user
                new_post.save()
                return redirect('index')
        else:
            form = NewPostForm(instance=None)
        return render(request, 'index.html',
                      {'form': form, 'posts': posts, 'online_users': online_users, 'page_obj': page_obj})
    else:
        return redirect('login')


def post_detail(request, pk):
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
        return render(request, 'post_detail.html', {'form': form,
                                                    'comments': comments,
                                                    'post': post,
                                                    'online_users': online_users,
                                                    'comments': comments})
    else:
        return redirect('login')


def delete_post(request, pk):
    post = Post.objects.get(pk=pk)
    if post.user.pk == request.user.pk:
        post.delete()
        return redirect('index')
    else:
        return HttpResponse('You can only delete your own posts')


def edit_post(request, pk):
    post = Post.objects.get(pk=pk)
    if request.method == 'POST':
        form = NewPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = NewPostForm(instance=post)
    return render(request, 'edit_post.html', {'form': form, 'post': post})


def like_post(request, pk):
    user = request.user
    post = Post.objects.get(pk=pk)
    if user in post.likers.all():
        post.likers.remove(user)
        post.save()
        return redirect(request.META.get('HTTP_REFERER'))
    elif user in post.dislikers.all() and user not in post.likers.all():
        post.likers.add(user)
        post.dislikers.remove(user)
        post.save()
    else:
        post.likers.add(user)
        post.save()
    return redirect(request.META.get('HTTP_REFERER'))


def dislike_post(request, pk):
    user = request.user
    post = Post.objects.get(pk=pk)
    if request.user in post.dislikers.all():
        post.dislikers.remove(user)
        post.save()
        return redirect(request.META.get('HTTP_REFERER'))
    elif user in post.likers.all() and user not in post.dislikers.all():
        post.dislikers.add(user)
        post.likers.remove(user)
        post.save()
    else:
        post.dislikers.add(user)
        post.save()
    return redirect(request.META.get('HTTP_REFERER'))

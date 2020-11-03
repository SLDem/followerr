from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.core.paginator import Paginator

from django import forms
from .forms import EditUserForm, ChangePasswordForm
from posts.forms import NewPostForm

from .models import User
from posts.models import Post
from friends.models import FriendRequest
from photoalbums.forms import NewImageForm
from photoalbums.models import Photoalbum

from authentication.views import see_online_users


def profile(request, pk):
    user = User.objects.get(pk=pk)
    if request.user in user.blocked_users.all():
        return HttpResponse('This user blocked you.')
    else:
        online_users = see_online_users()
        friends = user.friends.all()

        posts = Post.objects.filter(user=user).order_by('date_posted').reverse()
        posts_paginator = Paginator(posts, 5)
        page_number = request.GET.get('page')
        page_obj = posts_paginator.get_page(page_number)


        # Check if user is friend:
        button_status = 'none'
        if user not in request.user.friends.all():
            button_status = 'not_friend'
            if len(FriendRequest.objects.filter(from_user=request.user, to_user=user)) == 1:
                button_status = 'friend_request_sent'
        if user in request.user.friends.all():
            button_status = 'friend'

        if request.method == 'POST':
            form = NewPostForm(request.POST, request.FILES)
            if form.is_valid():
                new_post = form.save(commit=False)
                new_post.user = user
                new_post.save()
                return redirect('index')
        else:
            form = NewPostForm(instance=None)

        return render(request, 'profile.html', {'user': user, 'friends': friends, 'posts': posts, 'form': form,
                                                'button_status': button_status, 'online_users': online_users,
                                                'page_obj': page_obj})


def upload_avatar(request):
    if request.method == 'POST':
        form = NewImageForm(request.POST, request.FILES)
        if form.is_valid():

            photoalbum = Photoalbum.objects.filter(title='Profile pictures', user=request.user).first()
            if not photoalbum:
                photoalbum = Photoalbum.objects.create(title='Profile pictures', user=request.user)

            new_image = form.save(commit=False)
            new_image.album = photoalbum
            new_image.save()
            request.user.avatar = new_image
            request.user.save()
            return redirect('profile', pk=request.user.pk)
    else:
        form = NewImageForm()
    return render(request, 'upload_avatar.html', {'form': form})


def edit_user(request, pk):
    user = User.objects.get(pk=pk)
    if request.method == 'POST':
        form = EditUserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=user.pk)
    else:
        form = EditUserForm(instance=user)
    return render(request, 'edit_user.html', {'form': form, 'current_user': user})


def change_password(request):
    user = request.user
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            form.save(commit=False)
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            if password == confirm_password:
                user.set_password(password)
                user.save()
                return redirect('login')
            else:
                raise forms.ValidationError("Your passwords don't match")
    form = ChangePasswordForm()
    return render(request, 'edit_password.html', {'form': form})


def all_users_list(request):
    users = User.objects.exclude(pk=request.user.pk)
    return render(request, 'all_users_list.html', {'users': users})

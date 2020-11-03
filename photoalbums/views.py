from django.shortcuts import render, redirect, HttpResponse

from .models import Photoalbum, Image
from .forms import NewPhotoalbumForm, NewImageForm
from comments.models import Comment
from comments.forms import NewCommentForm
from user_profile.models import User

from authentication.views import see_online_users


def photoalbums(request, pk):
    user = User.objects.get(pk=pk)
    photoalbums = Photoalbum.objects.filter(user=user)

    if request.user == user:
        if request.method == 'POST':
            form = NewPhotoalbumForm(request.POST)
            if form.is_valid():
                new_album = form.save(commit=False)
                new_album.user = request.user
                new_album.save()
                form = NewPhotoalbumForm()
                return redirect('photoalbum', pk=new_album.pk)
        else:
            form = NewPhotoalbumForm()
    form = NewPhotoalbumForm()

    return render(request, 'photoalbums.html', {'photoalbums': photoalbums, 'form': form, 'user': user})


def photoalbum(request, pk):
    photoalbum = Photoalbum.objects.get(pk=pk)
    images = Image.objects.filter(album=photoalbum)
    if request.user == photoalbum.user:
        if request.method == 'POST':
            form = NewImageForm(request.POST, request.FILES)
            if form.is_valid():
                new_image = form.save(commit=False)
                new_image.album = photoalbum
                new_image.save()
                form = NewImageForm()
                return redirect('photoalbum', pk=photoalbum.pk)
        else:
            form = NewImageForm()
    form = NewImageForm()
    return render(request, 'photoalbum.html', {'photoalbum': photoalbum, 'form': form, 'images': images})


def image_detail(request, pk):
    online_users = see_online_users()
    image = Image.objects.get(pk=pk)
    comments = Comment.objects.filter(picture=image)
    if request.method == 'POST':
        form = NewCommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.parent_id = request.POST.get("parent_id")
            new_comment.picture = image
            new_comment.save()
            return redirect('image_detail', pk=image.pk)
    else:
        form = NewCommentForm()
    return render(request, 'image_detail.html', {'online_users': online_users,
                                                 'image': image,
                                                 'form': form,
                                                 'comments': comments})


def make_avatar(request, pk):
    image = Image.objects.get(pk=pk)
    if image.album.user == request.user and image != request.user.avatar:
        request.user.avatar = image
        request.user.save()
        return redirect('image_detail', pk=image.pk)
    else:
        return HttpResponse('Action not allowed')


def delete_image(request, pk):
    image = Image.objects.get(pk=pk)
    redirect_pk = image.album.pk
    if image.album.user == request.user:
        if image == request.user.avatar:
            request.user.avatar.delete()
        image.delete()
        return redirect('photoalbum', pk=redirect_pk)
    else:
        return HttpResponse('Action not allowed')


def edit_image(request, pk):
    image = Image.objects.get(pk=pk)
    if request.user == image.album.user:
        if request.method == 'POST':
            form = NewImageForm(request.POST, instance=image)
            if form.is_valid():
                form.save()
                return redirect('image_detail', pk=image.pk)
        else:
            form = NewImageForm(instance=image)
            return render(request, 'edit_image.html', {'image': image, 'form': form})
    else:
        return HttpResponse('Action not allowed')


def edit_album(request, pk):
    photoalbum = Photoalbum.objects.get(pk=pk)
    if request.user == photoalbum.user:
        if request.method == 'POST':
            form = NewPhotoalbumForm(request.POST, instance=photoalbum)
            if form.is_valid():
                form.save()
                form = NewPhotoalbumForm()
                return redirect('photoalbum', pk=photoalbum.pk)
        else:
            form = NewPhotoalbumForm(instance=photoalbum)
    else:
        return HttpResponse('Action not allowed')
    return render(request, 'edit_photoalbum.html', {'photoalbum': photoalbum, 'form': form})


def delete_album(request, pk):
    album = Photoalbum.objects.get(pk=pk)
    if album.user == request.user:
        album.delete()
        return redirect('photoalbums', pk=request.user.pk)
    else:
        return HttpResponse('Action not allowed')


def reply_form_picture(request, pk, parent_id):
    picture = Image.objects.get(pk=pk)
    if request.method == 'POST':
        form = NewCommentForm(request.POST)
        if form.is_valid():
            new_reply = form.save(commit=False)
            new_reply.user = request.user
            new_reply.parent_id = request.POST.get("parent_id")
            new_reply.picture = picture
            new_reply.save()
            return redirect('image_detail', pk=picture.pk)
    else:
        form = NewCommentForm()
    return render(request, 'reply_form_picture.html', {'picture': picture, 'form': form, 'parent_id': parent_id})


def like_image(request, pk):
    user = request.user
    image = Image.objects.get(pk=pk)
    if user in image.likers.all():
        image.likers.remove(user)
        image.save()
        return redirect(request.META.get('HTTP_REFERER'))
    elif user in image.dislikers.all() and user not in image.likers.all():
        image.likers.add(user)
        image.dislikers.remove(user)
        image.save()
    else:
        image.likers.add(user)
        image.save()
    return redirect(request.META.get('HTTP_REFERER'))


def dislike_image(request, pk):
    user = request.user
    image = Image.objects.get(pk=pk)
    if request.user in image.dislikers.all():
        image.dislikers.remove(user)
        image.save()
        return redirect(request.META.get('HTTP_REFERER'))
    elif user in image.likers.all() and user not in image.dislikers.all():
        image.dislikers.add(user)
        image.likers.remove(user)
        image.save()
    else:
        image.dislikers.add(user)
        image.save()
    return redirect(request.META.get('HTTP_REFERER'))

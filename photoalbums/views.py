from django.shortcuts import render, redirect, HttpResponse

from .models import Photoalbum, Image
from .forms import NewPhotoalbumForm, NewImageForm
from comments.models import Comment
from comments.forms import NewCommentForm
from user_profile.models import User

from authentication.views import see_online_users


def photoalbums(request, pk):
    try:
        user = User.objects.get(pk=pk)
        photoalbums = Photoalbum.objects.filter(user=user)
        title = user.name + 's photoalbums'
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
        else:
            return HttpResponse('Action not allowed')
        form = NewPhotoalbumForm()
        return render(request, 'photoalbums.html', {'photoalbums': photoalbums,
                                                    'form': form,
                                                    'user': user,
                                                    'title': title})
    except Exception:
        pass
    return HttpResponse('User does not exist')


def photoalbum(request, pk):
    try:
        photoalbum = Photoalbum.objects.get(pk=pk)
        title = photoalbum.title
        images = Image.objects.filter(album=photoalbum)
        if request.method == 'POST':
            if request.user == photoalbum.user:
                form = NewImageForm(request.POST, request.FILES)
                if form.is_valid():
                    new_image = form.save(commit=False)
                    new_image.album = photoalbum
                    new_image.save()
                    form = NewImageForm()
                    return redirect('photoalbum', pk=photoalbum.pk)
            else:
                return HttpResponse('Action not allowed')
        form = NewImageForm()
        return render(request, 'photoalbum.html', {'photoalbum': photoalbum,
                                                   'form': form,
                                                   'images': images,
                                                   'title': title})
    except Exception:
        pass
    return HttpResponse('Photoalbum does not exist')


def image_detail(request, pk):
    try:
        title = 'Image Detail'
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
                                                     'comments': comments,
                                                     'title': title})
    except Exception:
        pass
    return HttpResponse('Image does not exist')


def reply_form_picture(request, pk, parent_id):
    try:
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
    except Exception:
        pass
    return HttpResponse('Image does not exist')


def make_avatar(request, pk):
    try:
        image = Image.objects.get(pk=pk)
        if image.album.user == request.user and image != request.user.image:
            request.user.image = image
            request.user.save()
            return redirect('image_detail', pk=image.pk)
        else:
            return HttpResponse('Action not allowed')
    except Exception:
        pass
    return HttpResponse('Image does not exist')


def edit_image(request, pk):
    try:
        title = 'Edit Image'
        image = Image.objects.get(pk=pk)
        if request.user == image.album.user:
            if request.method == 'POST':
                form = NewImageForm(request.POST, instance=image)
                if form.is_valid():
                    form.save()
                    return redirect('image_detail', pk=image.pk)
            else:
                form = NewImageForm(instance=image)
                return render(request, 'edit_image.html', {'image': image, 'form': form, 'title': title})
        else:
            return HttpResponse('Action not allowed')
    except Exception:
        pass
    return HttpResponse('Image does not exist')


def delete_image(request, pk):
    try:
        image = Image.objects.get(pk=pk)
        photoalbum = image.album
        if image.album.user == request.user:
            if image == request.user.image:
                request.user.image.delete()
                image.delete()
            else:
                image.delete()
            return redirect('photoalbum', photoalbum.pk)
        else:
            return HttpResponse('Action not allowed')
    except Exception as ex:
        pass
    return HttpResponse('Image does not exist')


def edit_album(request, pk):
    try:
        photoalbum = Photoalbum.objects.get(pk=pk)
        title = 'Edit ' + photoalbum.title
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
        return render(request, 'edit_photoalbum.html', {'photoalbum': photoalbum,
                                                        'form': form,
                                                        'title': title})
    except Exception as ex:
        pass
    return HttpResponse('Photoalbum does not exist')


def delete_album(request, pk):
    try:
        album = Photoalbum.objects.get(pk=pk)
        if album.user == request.user:
            album.delete()
            return redirect('photoalbums', pk=request.user.pk)
        else:
            return HttpResponse('Action not allowed')
    except Exception as ex:
        print(ex)
    return HttpResponse('Photoalbum does not exist')


def like_image(request, pk):
    try:
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
    except Exception as ex:
        pass
    return HttpResponse('Image does not exist')


def dislike_image(request, pk):
    try:
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
    except Exception as ex:
        pass
    return HttpResponse('Image does not exist')
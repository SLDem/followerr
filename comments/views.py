from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import NewCommentForm

from posts.models import Post
from .models import Comment


def reply_form(request, pk, parent_id):
    try:
        post = Post.objects.get(pk=pk)
        if request.method == 'POST':
            form = NewCommentForm(request.POST)
            if form.is_valid():
                new_reply = form.save(commit=False)
                new_reply.user = request.user
                new_reply.parent_id = request.POST.get("parent_id")
                new_reply.post = post
                new_reply.save()
                return redirect('post_detail', pk=post.pk)
    except Exception as ex:
        pass
    return HttpResponse('Action not allowed')


def delete_comment(request, pk):
    try:
        comment = Comment.objects.get(pk=pk)
        post = comment.post
        if comment.user.pk == request.user.pk:
            comment.delete()
            return redirect('post_detail', pk=post.pk)
        else:
            return HttpResponse('You can only delete your own comments')

    except Exception as ex:
        pass
    return HttpResponse('Action not allowed')


def edit_comment(request, pk):
    try:
        comment = Comment.objects.get(pk=pk)
        post = comment.post
        if request.method == 'POST':
            form = NewCommentForm(request.POST, request.FILES, instance=comment)
            if form.is_valid():
                form.save()
                return redirect('post_detail', pk=post.pk)
        else:
            form = NewCommentForm(instance=comment)
        return render(request, 'edit_comment.html', {'form': form, 'comment': comment})

    except Exception as ex:
        pass
    return HttpResponse('Action not allowed')


def like_comment(request, pk):
    try:
        user = request.user
        comment = Comment.objects.get(pk=pk)
        post = comment.post
        if user in comment.likers.all():
            comment.likers.remove(user)
            comment.save()
            return redirect('post_detail', pk=post.pk)
        elif user in comment.dislikers.all() and user not in comment.likers.all():
            comment.likers.add(user)
            comment.dislikers.remove(user)
            comment.save()
        else:
            comment.likers.add(user)
            comment.save()
        return redirect('post_detail', pk=post.pk)

    except Exception as ex:
        pass
    return HttpResponse('Action not allowed')


def dislike_comment(request, pk):
    try:
        user = request.user
        comment = Comment.objects.get(pk=pk)
        post = comment.post
        if user in comment.dislikers.all():
            comment.dislikers.remove(user)
            comment.save()
            return redirect('post_detail', pk=post.pk)
        elif user in comment.likers.all() and user not in comment.dislikers.all():
            comment.dislikers.add(user)
            comment.likers.remove(user)
            comment.save()
        else:
            comment.dislikers.add(user)
            comment.save()
        return redirect('post_detail', pk=post.pk)

    except Exception as ex:
        pass
    return HttpResponse('Action not allowed')

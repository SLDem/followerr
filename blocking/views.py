from django.shortcuts import render, redirect
from django.http import HttpResponse

from user_profile.models import User
from friends.models import FriendRequest



def block_user(request, pk):
    user = request.user
    user_to_block = User.objects.get(pk=pk)

    user.blocked_users.add(user_to_block)
    to_f_request = FriendRequest.objects.filter(
        from_user=request.user,
        to_user=user_to_block
    ).first()
    f_request = FriendRequest.objects.filter(
        from_user=user_to_block,
        to_user=request.user
    ).first()

    if f_request:
        f_request.delete()
    if to_f_request:
        to_f_request.delete()

    if user_to_block in user.friends.all():
        user.friends.remove(user_to_block)
    user.save()
    return redirect(request.META.get('HTTP_REFERER'))


def unblock_user(request, pk):
    user = request.user
    user_to_unblock = User.objects.get(pk=pk)
    if user_to_unblock in user.blocked_users.all():
        user.blocked_users.remove(user_to_unblock)
        user.save()
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponse('You can not unblock someone you did not block')


def blocked_users(request):
    blocked_users = request.user.blocked_users.all()
    return render(request, 'blocked_users.html', {'blocked_users': blocked_users})
from django.shortcuts import render, redirect
from user_profile.models import User
from .models import FriendRequest
from authentication.views import see_online_users


def friends(request, pk):
    user = User.objects.get(pk=pk)
    friends = user.friends.all()
    sent_friend_requests = FriendRequest.objects.filter(from_user=request.user)
    received_friend_requests = FriendRequest.objects.filter(to_user=request.user)

    online_users = see_online_users()
    return render(request, 'friends.html', {'user': user,
                                            'friends': friends,
                                            'sent_friend_requests': sent_friend_requests,
                                            'received_friend_requests': received_friend_requests,
                                            'online_users': online_users,
                                            })


def send_friend_request(request, pk):
    if request.user.is_authenticated:
        user = User.objects.get(pk=pk)
        fr_request = FriendRequest.objects.filter(
            from_user=user,
            to_user=request.user
        )
        if fr_request:
            accept_friend_request(request, user.pk)
            fr_request.delete()
        else:
            f_request = FriendRequest.objects.create(
                from_user=request.user,
                to_user=user
            )
        return redirect(request.META.get('HTTP_REFERER'))


def cancel_friend_request(request, pk):
    if request.user.is_authenticated:
        user = User.objects.get(pk=pk)
        f_request = FriendRequest.objects.filter(
            from_user=request.user,
            to_user=user
        ).first()
        f_request.delete()
        return redirect(request.META.get('HTTP_REFERER'))


def accept_friend_request(request, pk):
    from_user = User.objects.get(pk=pk)
    f_request = FriendRequest.objects.filter(
        from_user=from_user,
        to_user=request.user
    ).first()
    user1 = f_request.to_user
    user2 = from_user
    user1.friends.add(user2)
    user2.friends.add(user1)
    f_request.delete()
    return redirect(request.META.get('HTTP_REFERER'))


def delete_friend_request(request, pk):
    from_user = User.objects.get(pk=pk)
    f_request = FriendRequest.objects.filter(
        from_user=from_user,
        to_user=request.user
    ).first()
    f_request.delete()
    return redirect(request.META.get('HTTP_REFERER'))


def remove_friend(request, pk):
    user = User.objects.get(pk=pk)
    current_user = User.objects.get(pk=request.user.pk)
    current_user.friends.remove(user)
    user.friends.remove(current_user)
    return redirect(request.META.get('HTTP_REFERER'))

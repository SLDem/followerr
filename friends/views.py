from django.shortcuts import render, redirect, HttpResponse

from .models import FriendRequest
from user_profile.models import User
from notifications.models import Notification

from authentication.views import see_online_users



def friends(request, pk):
    try:
        user = User.objects.get(pk=pk)
        title = user.name + 's Friends'
        friends = user.friends.all()
        sent_friend_requests = FriendRequest.objects.filter(from_user=request.user)
        received_friend_requests = FriendRequest.objects.filter(to_user=request.user)

        online_users = see_online_users()
        return render(request, 'friends/friends.html', {'user': user,
                                                'friends': friends,
                                                'sent_friend_requests': sent_friend_requests,
                                                'received_friend_requests': received_friend_requests,
                                                'online_users': online_users,
                                                'title': title
                                                })
    except Exception as ex:
        pass
    return HttpResponse('User does not exist')


def send_friend_request(request, pk):
    try:
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
                Notification.objects.create(type='FR',
                                            text='Friend Request from ' + user.name,
                                            user=user,
                                            friend_request=f_request)
            return redirect('profile', pk=user.pk)

    except Exception as ex:
        pass
    return HttpResponse('User does not exist')


def cancel_friend_request(request, pk):
    try:
        if request.user.is_authenticated:
            user = User.objects.get(pk=pk)
            f_request = FriendRequest.objects.filter(
                from_user=request.user,
                to_user=user
            ).first()
            notification = Notification.objects.filter(friend_request=f_request)
            f_request.delete()
            notification.delete()

            return redirect('profile', pk=user.pk)
    except Exception as ex:
        pass
    return HttpResponse('User does not exist')


def accept_friend_request(request, pk):
    try:
        from_user = User.objects.get(pk=pk)
        f_request = FriendRequest.objects.filter(
            from_user=from_user,
            to_user=request.user
        ).first()
        user1 = request.user
        user2 = from_user
        user1.friends.add(user2)
        user2.friends.add(user1)
        f_request.delete()
        return redirect(request.META.get('HTTP_REFERER', '/'))
    except Exception:
        pass
    return HttpResponse('User does not exist')


def delete_friend_request(request, pk):
    try:
        from_user = User.objects.get(pk=pk)
        f_request = FriendRequest.objects.filter(
            from_user=from_user,
            to_user=request.user
        ).first()
        f_request.delete()
        return redirect(request.META.get('HTTP_REFERER', '/'))
    except Exception:
        pass
    return HttpResponse('User does not exist')


def remove_friend(request, pk):
    try:
        user = User.objects.get(pk=pk)
        current_user = request.user
        current_user.friends.remove(user)
        user.friends.remove(current_user)
        return redirect(request.META.get('HTTP_REFERER', '/'))
    except Exception:
        pass
    return HttpResponse('User does not exist')

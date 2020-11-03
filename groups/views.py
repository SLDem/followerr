from django.shortcuts import render, redirect
from django.http import HttpResponse

from .models import GroupJoinRequest, Discussion, Group
from user_profile.models import User
from posts.models import Post
from chats.models import Message

from authentication.views import see_online_users

from posts.forms import NewPostForm
from chats.forms import NewMessageForm
from .forms import NewGroupForm, NewDiscussionForm


def groups(request):
    user = request.user
    user_groups = Group.objects.filter(users__id=user.pk)
    all_groups = Group.objects.all()

    if request.method == 'POST':
        form = NewGroupForm(request.POST, request.FILES)
        if form.is_valid():
            new_group = form.save(commit=False)
            new_group.admin = user
            new_group.save()
            new_group.owners.add(user)
            new_group.users.add(user)
            form = NewGroupForm()
            return redirect('group_detail', pk=new_group.pk)
    else:
        form = NewGroupForm()
    return render(request, 'groups.html', {'all_groups': all_groups, 'user_groups': user_groups, 'form': form})


def group_detail(request, pk):
    user = request.user
    group = Group.objects.get(pk=pk)
    posts = Post.objects.filter(group=group)
    users = User.objects.filter(id__in=group.users.all())[:4]
    discussions = Discussion.objects.filter(group=group)[:3]

    button_status = 'none'
    if user not in group.users.all():
        button_status = 'not_in_group'
        if len(GroupJoinRequest.objects.filter(from_user=request.user, to_group=group)) == 1:
            button_status = 'group_join_request_sent'
    if user in request.user.friends.all():
        button_status = 'joined'

    if request.method == 'POST':
        form = NewPostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.group = group
            new_post.save()
            return redirect('group_detail', pk=group.pk)
    else:
        form = NewPostForm()
    return render(request, 'group_detail.html', {'group': group,
                                                 'form': form,
                                                 'posts': posts,
                                                 'button_status': button_status,
                                                 'users': users,
                                                 'discussions': discussions})


def group_management(request, pk):
    group = Group.objects.get(pk=pk)
    join_requests = GroupJoinRequest.objects.filter(to_group=group)
    if request.user in group.owners.all():
        if request.method == 'POST':
            form = NewGroupForm(request.POST, request.FILES, instance=group)
            if form.is_valid():
                form.save()
                return redirect('group_detail', pk=group.pk)
        else:
            form = NewGroupForm(instance=group)
        return render(request, 'group_management.html', {'join_requests': join_requests, 'group': group, 'form': form})
    else:
        return HttpResponse('You can only manage your own groups.')


def discussions_list(request, pk):
    group = Group.objects.get(pk=pk)
    discussions = Discussion.objects.filter(group=group)
    if request.method == 'POST':
        form = NewDiscussionForm(request.POST)
        if form.is_valid():
            new_discussion = form.save(commit=False)
            new_discussion.author = request.user
            new_discussion.group = group
            new_discussion.save()
            form = NewDiscussionForm()
            return redirect('discussion', pk=new_discussion.pk)
    else:
        form = NewDiscussionForm()
    return render(request, 'discussions.html', {'form': form, 'group': group, 'discussions': discussions})


def discussion(request, pk):
    discussion = Discussion.objects.get(pk=pk)
    messages = Message.objects.filter(discussion=discussion)
    online_users = see_online_users()
    if request.method == 'POST':
        form = NewMessageForm(request.POST, request.FILES)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.discussion = discussion
            new_message.from_user = request.user
            new_message.save()
            form = NewMessageForm()
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        form = NewMessageForm()
    return render(request, 'discussion.html', {'form': form,
                                               'discussion': discussion,
                                               'messages': messages,
                                               'online_users': online_users})


def remove_discussion(request, pk):
    discussion = Discussion.objects.get(pk=pk)
    redirect_pk = discussion.group.pk
    if discussion.group.admin == request.user or discussion.author == request.user:
        discussion.delete()
        return redirect(request, 'discussions', pk=redirect_pk)
    else:
        return HttpResponse('You can not remove this discussion unless you are its author or group admin.')


def group_users(request, pk):
    group = Group.objects.get(pk=pk)
    return render(request, 'group_users.html', {'group': group})


def join_or_leave_group(request, pk):
    user = request.user
    group = Group.objects.get(pk=pk)
    if user in group.users.all():
        if user in group.owners.all():
            group.owners.remove(user)
            group.save()
        group.users.remove(user)
        group.save()
    else:
        if not group.is_private:
            group.users.add(user)
            group.save()
        else:
            return HttpResponse('This group is private')
    if group.users.count() == 0:
        group.delete()
        return redirect('groups')
    return redirect('group_detail', pk=group.pk)


def delete_group(request, pk):
    user = request.user
    group = Group.objects.get(pk=pk)
    if user == group.admin:
        group.delete()
        return redirect('groups')
    else:
        return HttpResponse('You can only delete groups you are admin of')


def send_group_request(request, pk):
    group = Group.objects.get(pk=pk)
    g_request = GroupJoinRequest.objects.create(
        to_group=group,
        from_user=request.user
    )
    return redirect(request.META.get('HTTP_REFERER'))


def cancel_group_request(request, pk):
    group = Group.objects.get(pk=pk)
    g_request = GroupJoinRequest.objects.filter(
        from_user=request.user,
        to_group=group
    ).first()
    g_request.delete()
    return redirect(request.META.get('HTTP_REFERER'))


def accept_group_request(request, pk, user_pk):
    group = Group.objects.get(pk=pk)
    from_user = User.objects.get(pk=user_pk)
    g_request = GroupJoinRequest.objects.filter(
        from_user=from_user,
        to_group=group
    ).first()
    group.users.add(from_user)
    g_request.delete()
    group.save()
    return redirect(request.META.get('HTTP_REFERER'))


def delete_group_request(request, pk, user_pk):
    group = Group.objects.get(pk=pk)
    from_user = User.objects.get(pk=user_pk)
    g_request = GroupJoinRequest.objects.filter(
        from_user=from_user,
        to_group=group
    ).first()
    g_request.delete()
    return redirect(request.META.get('HTTP_REFERER'))


def make_owner(request, pk, user_pk):
    group = Group.objects.get(pk=pk)
    user = User.objects.get(pk=user_pk)
    if request.user in group.owners.all():
        group.owners.add(user)
        group.save()
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponse('You can only edit your own groups')


def remove_owner(request, pk, user_pk):
    group = Group.objects.get(pk=pk)
    group_participant = User.objects.get(pk=user_pk)
    if request.user == group.admin:
        group.owners.remove(group_participant)
        return redirect('group_management', pk=group.pk)
    else:
        return HttpResponse('You cant perform this action unless you are the admin of this group')


def remove_user_from_group(request, pk, user_pk):
    group = Group.objects.get(pk=pk)
    user_to_remove = User.objects.get(pk=user_pk)
    if request.user in group.owners.all():
        if user_to_remove in group.owners.all():
            return HttpResponse('You can not remove other owners')
        else:
            group.users.remove(user_to_remove)
            group.save()
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        return HttpResponse('You can only remove users from your own groups')

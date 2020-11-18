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

from search.documents import GroupDocument


def groups(request):
    user = request.user
    user_groups = Group.objects.filter(users__id=user.pk)
    all_groups = Group.objects.all()
    title = 'Groups'

    def search_groups(request):
        q = request.GET.get('q')

        if q:
            searched_groups = GroupDocument.search().query('match', title=q)
        else:
            searched_groups = ''
        return searched_groups

    searched_groups = search_groups(request)

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
    return render(request, 'groups/groups.html', {'all_groups': all_groups,
                                                  'searched_groups': searched_groups,
                                                  'user_groups': user_groups,
                                                  'form': form,
                                                  'title': title})


def group_detail(request, pk):
    try:
        user = request.user
        group = Group.objects.get(pk=pk)
        posts = Post.objects.filter(group=group)
        users = User.objects.filter(id__in=group.users.all())[:4]
        discussions = Discussion.objects.filter(group=group)[:3]

        if group.is_private:
            button_status = 'none'
            if user not in group.users.all():
                button_status = 'not_in_group'
                if len(GroupJoinRequest.objects.filter(from_user=request.user, to_group=group)) == 1:
                    button_status = 'group_join_request_sent'
            if user in group.users.all():
                button_status = 'joined'
        else:
            button_status = 'none'

        if request.method == 'POST':
            if request.user in group.owners.all() or request.user == group.admin:
                form = NewPostForm(request.POST, request.FILES)
                if form.is_valid():
                    new_post = form.save(commit=False)
                    new_post.group = group
                    new_post.save()
                    return redirect('group_detail', pk=group.pk)
            else:
                return HttpResponse('Action not allowed')
        else:
            form = NewPostForm()
        return render(request, 'groups/group_detail.html', {'group': group,
                                                            'form': form,
                                                            'posts': posts,
                                                            'button_status': button_status,
                                                            'users': users,
                                                            'discussions': discussions,
                                                            'title': group.title})
    except Exception:
        pass
    return HttpResponse('Group does not exist')


def discussions_list(request, pk):
    try:
        group = Group.objects.get(pk=pk)
        title = "Discussions of " + group.title + " group"
        discussions = Discussion.objects.filter(group=group)
        if request.method == 'POST':
            if request.user in group.users.all():
                form = NewDiscussionForm(request.POST)
                if form.is_valid():
                    new_discussion = form.save(commit=False)
                    new_discussion.author = request.user
                    new_discussion.group = group
                    new_discussion.save()
                    form = NewDiscussionForm()
                    return redirect('discussion', pk=new_discussion.pk)
            else:
                return HttpResponse('You have to be a member of the group to create discussions')
        else:
            form = NewDiscussionForm()
        return render(request, 'groups/discussions.html', {'form': form,
                                                    'group': group,
                                                    'discussions': discussions,
                                                    'title': title})

    except Exception:
        pass
    return HttpResponse('Group does not exist')


def discussion(request, pk):
    try:
        discussion = Discussion.objects.get(pk=pk)
        group = discussion.group
        messages = Message.objects.filter(discussion=discussion)
        online_users = see_online_users()
        if request.method == 'POST':
            if request.user in group.users.all():
                form = NewMessageForm(request.POST, request.FILES)
                if form.is_valid():
                    new_message = form.save(commit=False)
                    new_message.discussion = discussion
                    new_message.from_user = request.user
                    new_message.save()
                    form = NewMessageForm()
                    return redirect(request.META.get('HTTP_REFERER', '/'))
            else:
                return HttpResponse('You must be a member of the group to post messages in this discussion')
        else:
            form = NewMessageForm()
        return render(request, 'groups/discussion.html', {'form': form,
                                                   'discussion': discussion,
                                                   'messages': messages,
                                                   'online_users': online_users,
                                                   'title': discussion.title})
    except Exception:
        pass
    return HttpResponse('Discussion does not exist')


def remove_discussion(request, pk):
    try:
        discussion = Discussion.objects.get(pk=pk)
        redirect_pk = discussion.group.pk
        if discussion.group.admin == request.user or discussion.author == request.user:
            discussion.delete()
            return redirect('discussions_list', pk=redirect_pk)
        else:
            return HttpResponse('You can not remove this discussion unless you are its author or group admin.')
    except Exception:
        pass
    return HttpResponse('Discussion does not exist')


def join_or_leave_group(request, pk):
    try:
        user = request.user
        group = Group.objects.get(pk=pk)
        if user in group.users.all():
            if user in group.owners.all():
                group.owners.remove(user)
            group.users.remove(user)
        else:
            if not group.is_private:
                group.users.add(user)
            else:
                return HttpResponse('This group is private')
        if user == group.admin:
            return HttpResponse('You can not leave your own group, you must delete it')
        return redirect('group_detail', pk=group.pk)
    except Exception:
        pass
    return HttpResponse('Group does not exist')


def send_group_request(request, pk):
    try:
        group = Group.objects.get(pk=pk)
        if group.is_private:
            g_request = GroupJoinRequest.objects.create(
                to_group=group,
                from_user=request.user
            )
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            return HttpResponse('This group is not private')
    except Exception:
        pass
    return HttpResponse('Group does not exist')


def cancel_group_request(request, pk):
    try:
        group = Group.objects.get(pk=pk)
        if group.is_private:
            g_request = GroupJoinRequest.objects.filter(
                from_user=request.user,
                to_group=group
            ).first()
            if g_request:
                g_request.delete()
            else:
                return HttpResponse('Group join request does not exist')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            return HttpResponse('Group is not private')
    except Exception:
        pass
    return HttpResponse('Group does not exist')


def accept_group_request(request, pk, user_pk):
    try:
        group = Group.objects.get(pk=pk)
        if request.user in group.owners.all() or request.user == group.admin:
            from_user = User.objects.get(pk=user_pk)
            g_request = GroupJoinRequest.objects.filter(
                from_user=from_user,
                to_group=group
            ).first()
            group.users.add(from_user)
            g_request.delete()
            group.save()
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            return HttpResponse('Action not allowed')
    except Exception:
        pass
    return HttpResponse('Group, user or join request does not exist')


def delete_group_request(request, pk, user_pk):
    try:
        group = Group.objects.get(pk=pk)
        if request.user in group.owners.all() or request.user == group.admin:
            from_user = User.objects.get(pk=user_pk)
            g_request = GroupJoinRequest.objects.filter(
                from_user=from_user,
                to_group=group
            ).first()
            g_request.delete()
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            return HttpResponse('Action not allowed')
    except Exception:
        pass
    return HttpResponse('Group, user or join request does not exist')


def group_management(request, pk):
    try:
        group = Group.objects.get(pk=pk)
        title = 'Group ' + group.title + ' management'
        join_requests = GroupJoinRequest.objects.filter(to_group=group)
        if request.user in group.owners.all():
            if request.method == 'POST':
                form = NewGroupForm(request.POST, request.FILES, instance=group)
                if form.is_valid():
                    form.save()
                    group.save()
                    return redirect('group_detail', pk=group.pk)
            else:
                form = NewGroupForm(instance=group)
            return render(request, 'groups/group_management.html', {'join_requests': join_requests,
                                                             'group': group,
                                                             'form': form,
                                                             'title': title})
        else:
            return HttpResponse('You can only manage your own groups.')
    except Exception:
        pass
    return HttpResponse('Group does not exist')


def group_users(request, pk):
    try:
        group = Group.objects.get(pk=pk)
        title = group.title + ' participants'
        if not group.is_private:
            return render(request, 'groups/group_users.html', {'group': group, 'title': title})
        elif group.is_private and request.user in group.users.all():
            return render(request, 'groups/group_users.html', {'group': group, 'title': title})
        else:
            return HttpResponse('You must be a member of this group to view its participants')
    except Exception:
        pass
    return HttpResponse('Group does not exist')


def remove_user_from_group(request, pk, user_pk):
    try:
        group = Group.objects.get(pk=pk)
        user_to_remove = User.objects.get(pk=user_pk)
        if request.user == group.admin:
            if user_to_remove in group.owners.all():
                group.owners.remove(user_to_remove)
                group.users.remove(user_to_remove)
            else:
                group.users.remove(user_to_remove)
                return redirect(request.META.get('HTTP_REFERER', '/'))
        elif request.user in group.owners.all():
            if user_to_remove in group.owners.all() or user_to_remove == group.admin:
                return HttpResponse('You can not remove other owners or admin')
            else:
                group.users.remove(user_to_remove)
                return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            return HttpResponse('You can only remove users from your own groups')
    except Exception:
        pass
    return HttpResponse('Group or user does not exist')


def delete_group(request, pk):
    try:
        user = request.user
        group = Group.objects.get(pk=pk)
        if user == group.admin:
            group.delete()
            return redirect('groups')
        else:
            return HttpResponse('You can only delete groups you are admin of')
    except Exception:
        pass
    return HttpResponse('Group does not exist')



def make_owner(request, pk, user_pk):
    try:
        group = Group.objects.get(pk=pk)
        user = User.objects.get(pk=user_pk)
        if request.user in group.owners.all() or request.user == group.admin:
            if user in group.owners.all() or user == group.admin:
                return HttpResponse('User already listed as owner of the group')
            else:
                group.owners.add(user)
                group.save()
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            return HttpResponse('Action not allowed')
    except Exception:
        pass
    return HttpResponse('User or group does not exist')


def remove_owner(request, pk, user_pk):
    try:
        group = Group.objects.get(pk=pk)
        group_participant = User.objects.get(pk=user_pk)
        if request.user == group.admin:
            if group_participant == group.admin:
                return HttpResponse('You cant remove your own owner rights')
            elif group_participant not in group.owners.all():
                return HttpResponse('This user is not the owner of the group')
            group.owners.remove(group_participant)
            return redirect('group_management', pk=group.pk)
        else:
            return HttpResponse('You cant perform this action unless you are the admin of this group')
    except Exception:
        pass
    return HttpResponse('User or group does not exist')


from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.paginator import Paginator

from .forms import NewMessageForm, NewChatForm, AddUsersToChatForm, NewPrivateMessageForm
from user_profile.models import User
from .models import Message, PrivateMessage, Chat
from authentication.views import see_online_users
from django.contrib.auth.decorators import login_required


def get_users_for_private_messages(request):
    users = []
    for message in PrivateMessage.objects.filter(from_user=request.user):
        users.append(message.to_user)
    for message in PrivateMessage.objects.filter(to_user=request.user):
        users.append(message.from_user)
    users = set(users)
    return users


@login_required
def messages(request):
    user = request.user
    online_users = see_online_users()
    users = get_users_for_private_messages(request)
    chats = Chat.objects.filter(users__id=user.pk)

    # creating chats
    if request.method == 'POST':
        form = NewChatForm(request.POST, request.FILES)
        if form.is_valid():
            new_chat = form.save(commit=False)
            new_chat.owner = user
            new_chat.save()
            new_chat.users.add(user)
            return redirect('messages')
    else:
        form = NewChatForm(None)
    return render(request, 'messages.html', {'online_users': online_users, 'chats': chats, 'form': form, 'users': users})


def delete_message(request, pk):
    try:
        message = Message.objects.get(pk=pk)
        if request.user == message.from_user:
            message.delete()
        return redirect(request.get_full_path())
    except Exception as ex:
        pass
    return redirect('messages')


def chat(request, pk):
    online_users = see_online_users()
    chat = Chat.objects.get(pk=pk)
    messages = Message.objects.filter(chat=chat)

    messages_paginator = Paginator(messages, 10)
    page_number = request.GET.get('page')
    page_obj = messages_paginator.get_page(page_number)

    if request.method == 'POST':
        form = NewMessageForm(request.POST, request.FILES)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.from_user = request.user
            new_message.chat = chat
            new_message.save()
            form = NewMessageForm()
            redirect('chat', pk=chat.pk)
    else:
        form = NewMessageForm()
    return render(request, 'chat.html', {'messages': messages,
                                         'form': form,
                                         'online_users': online_users,
                                         'chat': chat,
                                         'page_obj': page_obj})


def edit_chat(request, pk):
    chat = Chat.objects.get(pk=pk)
    if request.user == chat.owner:
        if request.method == 'POST':
            form = NewChatForm(request.POST, request.FILES, instance=chat)
            form.save()
            return redirect('chat', pk=chat.pk)
        else:
            form = NewChatForm(instance=chat)
            return render(request, 'edit_chat.html', {'form': form, 'chat': chat})
    else:
        return HttpResponse('You must be the owner of the chat to edit it.')


def delete_chat(request, pk):
    try:
        chat = Chat.objects.get(pk=pk)
        if request.user == chat.owner:
            chat.delete()
            return redirect('messages')
        else:
            return HttpResponse('You can only delete your own chats')
    except Exception as ex:
        pass
    return HttpResponse('You can not delete a chat that does not exist')


def add_users_to_chat(request, pk):
    try:
        chat = Chat.objects.get(pk=pk)

        friends = request.user.friends.all()
        chat_users = chat.users.all()

        queryset = friends.exclude(id__in=chat_users)
        if request.user == chat.owner:
            if request.method == 'POST':
                form = AddUsersToChatForm(queryset, request.POST)
                if form.is_valid():
                    users_to_add = form.cleaned_data['users']
                    chat.users.add(*users_to_add)
                    chat.save()
                    return redirect('messages')
            else:
                form = AddUsersToChatForm(queryset)
            return render(request, 'add_users_to_chat.html', {'form': form, 'chat': chat, 'friends': friends})
        else:
            return HttpResponse('You can only edit your own chats')
    except Exception as ex:
        pass
    return redirect('messages')


def chat_users(request, pk):
    chat = Chat.objects.get(pk=pk)
    users = chat.users.all()
    return render(request, 'chat_users.html', {'users': users, 'chat': chat})


def remove_user_from_chat(request, pk, user_pk):
    try:
        chat = Chat.objects.get(pk=pk)
        user = User.objects.get(pk=user_pk)
        if user in chat.users.all() and request.user == chat.owner:
            chat.users.remove(user)
            chat.save()
            return redirect('chat_users', pk=chat.pk)
        else:
            return HttpResponse('Action not allowed')
    except Exception as ex:
        pass
    return HttpResponse('User or chat does not exist')


def leave_chat(request, pk):
    try:
        chat = Chat.objects.get(pk=pk)
        user = request.user
        chat.users.remove(user)
        if len(chat.users.all() == 0):
            chat.delete()
        chat.save()
        return redirect('messages')
    except Exception as ex:
        pass
    return HttpResponse('This chat does not exist yet or have been deleted')


def private_messages(request, pk):
    online_users = see_online_users()
    receiver = User.objects.get(pk=pk)

    from_user = PrivateMessage.objects.filter(from_user=request.user, to_user=receiver)
    to_user = PrivateMessage.objects.filter(to_user=request.user, from_user=receiver)
    messages = from_user.union(to_user)

    messages_paginator = Paginator(messages, 10)
    page_number = request.GET.get('page')
    page_obj = messages_paginator.get_page(page_number)

    if request.method == 'POST':
        form = NewPrivateMessageForm(request.POST, request.FILES)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.from_user = request.user
            new_message.to_user = receiver
            new_message.save()
            form = NewPrivateMessageForm()
            return redirect('private_messages', pk=receiver.pk)
    else:
        form = NewPrivateMessageForm()
    return render(request, 'private_messages.html', {'online_users': online_users,
                                                     'messages': messages,
                                                     'form': form,
                                                     'receiver': receiver,
                                                     'page_obj': page_obj})


def delete_private_message(request, pk):
    try:
        message = PrivateMessage.objects.get(pk=pk)
        if request.user == message.from_user or request.user == message.to_user:
            message.delete()
            return redirect(request.get_full_path())
        else:
            return HttpResponse('Action not allowed')
    except Exception as ex:
        pass
    return HttpResponse('Action not allowed')

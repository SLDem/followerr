from django.shortcuts import render, redirect
from django.http import HttpResponse

from .forms import NewMessageForm, NewChatForm, AddUserToChatForm, NewPrivateMessageForm
from user_profile.models import User
from .models import Message, PrivateMessage, Chat
from authentication.views import see_online_users


def get_users_for_private_messages(request):
    users = []
    for message in PrivateMessage.objects.filter(from_user=request.user):
        users.append(message.to_user)
    for message in PrivateMessage.objects.filter(to_user=request.user):
        users.append(message.from_user)
    users = set(users)
    return users


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
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        form = NewChatForm(None)
    return render(request, 'messages.html', {'online_users': online_users, 'chats': chats, 'form': form, 'users': users})


def chat(request, pk):
    online_users = see_online_users()
    chat = Chat.objects.get(pk=pk)
    messages = Message.objects.filter(chat=chat)
    if request.method == 'POST':
        form = NewMessageForm(request.POST, request.FILES)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.from_user = request.user
            new_message.chat = chat
            new_message.save()
            form = NewMessageForm()
            redirect(request.META.get('HTTP_REFERER'))
    else:
        form = NewMessageForm()
    return render(request, 'chat.html', {'messages': messages, 'form': form, 'online_users': online_users, 'chat': chat})


def private_messages(request, pk):
    online_users = see_online_users()
    receiver = User.objects.get(pk=pk)

    from_user = PrivateMessage.objects.filter(from_user=request.user, to_user=receiver)
    to_user = PrivateMessage.objects.filter(to_user=request.user, from_user=receiver)
    messages = from_user.union(to_user)

    if request.method == 'POST':
        form = NewPrivateMessageForm(request.POST, request.FILES)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.from_user = request.user
            new_message.to_user = receiver
            new_message.save()
            form = NewPrivateMessageForm()
            redirect(request.META.get('HTTP_REFERER'))
    else:
        form = NewPrivateMessageForm()
    return render(request, 'private_messages.html', {'online_users': online_users, 'messages': messages, 'form': form, 'receiver': receiver})


def chat_users(request, pk):
    chat = Chat.objects.get(pk=pk)
    users = chat.users.all()
    return render(request, 'chat_users.html', {'users': users, 'chat': chat})


def remove_user_from_chat(request, pk, user_pk):
    chat = Chat.objects.get(pk=pk)
    user = User.objects.get(pk=user_pk)
    chat.users.remove(user)
    chat.save()
    return redirect(request.META.get('HTTP_REFERER'))


def add_users_to_chat(request, pk):
    chat = Chat.objects.get(pk=pk)

    friends = request.user.friends.all()
    chat_users = chat.users.all()

    queryset = friends.exclude(id__in=chat_users)

    if request.method == 'POST':
        form = AddUserToChatForm(queryset, request.POST)
        if form.is_valid():
            users_to_add = form.cleaned_data['users']
            chat.users.add(*users_to_add)
            chat.save()
            return redirect('messages')
    else:
        form = AddUserToChatForm(queryset)
    return render(request, 'add_users_to_chat.html', {'form': form, 'chat': chat, 'friends': friends})


def leave_chat(request, pk):
    chat = Chat.objects.get(pk=pk)
    user = request.user
    chat.users.remove(user)
    chat.save()
    return redirect('messages')


def delete_message(request, pk):
    message = Message.objects.get(pk=pk)
    if request.user == message.from_user:
        message.delete()
    return redirect(request.META.get('HTTP_REFERER'))


def delete_private_message(request, pk):
    message = PrivateMessage.objects.get(pk=pk)
    if request.user == message.from_user or request.user == message.to_user:
        message.delete()
    return redirect(request.META.get('HTTP_REFERER'))


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
    chat = Chat.objects.get(pk=pk)
    if request.user == chat.owner:
        chat.delete()
        return redirect('messages')
    else:
        return HttpResponse('You can only delete your own chats')

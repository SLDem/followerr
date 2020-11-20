from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.forms import forms

from .forms import NewMessageForm, NewChatForm, AddUsersToChatForm

from .models import Message, Chat
from user_profile.models import User
from notifications.models import Notification

from search.documents import MessageDocument

from authentication.views import see_online_users



def messages(request):
    title = 'Chats'
    user = request.user
    online_users = see_online_users()
    chats = Chat.objects.filter(users__id=user.pk)

    for chat in chats:
        for message in chat.chat_messages.all():
            if not message.is_read:
                chat.unread_count += 1

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
    return render(request, 'chats/messages.html', {'online_users': online_users,
                                             'chats': chats,
                                             'form': form,
                                             'title': title})


def create_private_chat(request, pk):
    user = User.objects.get(pk=pk)
    chat = Chat.objects.filter(users__id=user.pk, is_private=True).filter(users__id=request.user.pk).first()
    if chat:
        return redirect('chat', pk=chat.pk)
    else:
        chat = Chat.objects.create(is_private=True)
        chat.users.add(user)
        chat.users.add(request.user)
        return redirect('chat', pk=chat.pk)


def delete_message(request, pk):
    try:
        message = Message.objects.get(pk=pk)
        redirect_pk = message.chat.pk
        chat = message.chat
        if request.user == message.from_user:
            if message == chat.last_message:
                message.delete()
                if chat.chat_messages.count() == 0:
                    return redirect('chat', pk=redirect_pk)
                else:
                    chat.last_message = chat.chat_messages.latest('created_at')
                    chat.save()
            else:
                message.delete()
                chat.save()
        else:
            return HttpResponse('Action not allowed')
        return redirect(request.META.get('HTTP_REFERER', '/'))
    except Exception as ex:
        return HttpResponse(ex)


def chat(request, pk):
    def search_messages(request):
        q = request.GET.get('q')

        if q:
            searched_messages = MessageDocument.search().query('match', body=q)
        else:
            searched_messages = ''
        return searched_messages

    searched_messages = search_messages(request)

    online_users = see_online_users()
    chat = Chat.objects.get(pk=pk)
    messages = Message.objects.filter(chat=chat)

    form = NewMessageForm()

    if chat.is_private:
        title = 'Chat'
    else:
        title = chat.title

    if request.method == 'GET':
        for message in messages:
            if message.from_user != request.user:
                message.is_read = True
                message.save()
        for n in Notification.objects.filter(user=request.user, message__in=chat.chat_messages.all()):
            n.delete()

    if request.method == 'POST':
        form = NewMessageForm(request.POST, request.FILES)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.from_user = request.user
            new_message.chat = chat
            new_message.save()
            chat.last_message = new_message
            for notification in Notification.objects.filter(message__chat=chat).all():
                notification.delete()
            for user in chat.users.all():
                if user != request.user:
                    notification = Notification.objects.create(type='M',
                                                               text='New Message',
                                                               user=user,
                                                               message=new_message)
                    notification.save()
            chat.save()
            form = NewMessageForm()
            return redirect(reverse('chat', kwargs={'pk': chat.pk}))
    return render(request, 'chats/chat.html', {'messages': messages,
                                               'form': form,
                                               'online_users': online_users,
                                               'chat': chat,
                                               'title': title,
                                               'searched_messages': searched_messages})


def edit_chat(request, pk):
    chat = Chat.objects.get(pk=pk)
    title = 'Edit ' + chat.title
    if request.user == chat.owner:
        if request.method == 'POST':
            form = NewChatForm(request.POST, request.FILES, instance=chat)
            form.save()
            return redirect('chat', pk=chat.pk)
        else:
            form = NewChatForm(instance=chat)
            return render(request, 'edit_chat.html', {'form': form, 'chat': chat, 'title': title})
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
        if chat.is_private:
            return HttpResponse('This chat is private')
        title = "Add Users"

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
            return render(request, 'chats/add_users_to_chat.html', {'form': form, 'chat': chat, 'friends': friends, 'title': title})
        else:
            return HttpResponse('You can only edit your own chats')
    except Exception as ex:
        pass
    return redirect('messages')



def chat_users(request, pk):
    try:
        chat = Chat.objects.get(pk=pk)
        title = "Participants"
        if request.user in chat.users.all():
            users = chat.users.all()
            return render(request, 'chats/chat_users.html', {'users': users, 'chat': chat, 'title': title})
        else:
            return HttpResponse('Action not allowed')
    except Exception as ex:
        pass
    return HttpResponse('Chat does not exist')


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


from django.shortcuts import render
from search.documents import ChatDocument, PrivateMessageDocument, PhotoalbumDocument, \
    ImageDocument, UserDocument


def search_chats(request):
    q = request.GET.get('q')
    title = 'Search Chats'
    if q:
        chats = ChatDocument.search().query('match', title=q)
    else:
        chats = ''
    return render(request, 'search_chats.html', {'chats': chats, 'title': title})


def search_private_messages(request):
    q = request.GET.get('q')
    title = 'Search Private Messages'
    if q:
        private_messages = PrivateMessageDocument.search().query('match', body=q)
    else:
        private_messages = ''
    return render(request, 'search_private_messages.html', {'private_messages': private_messages, 'title': title})


def search_photoalbums(request):
    q = request.GET.get('q')
    title = 'Search Photoalbums'
    if q:
        photoalbums = PhotoalbumDocument.search().query('match', title=q)
    else:
        photoalbums = ''
    return render(request, 'search_photoalbums.html', {'photoalbums': photoalbums, 'title': title})


def search_images(request):
    q = request.GET.get('q')
    title = 'Search Images'
    if q:
        images = ImageDocument.search().query('match', description=q)
    else:
        images = ''
    return render(request, 'search_images.html', {'images': images, 'title': title})


def search_users(request):
    q = request.GET.get('q')
    title = 'Search Users'
    if q:
        users = UserDocument.search().query('match', name=q)
    else:
        users = ''
    return render(request, 'search_users.html', {'users': users, 'title': title})

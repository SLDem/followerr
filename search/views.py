from django.shortcuts import render
from search.documents import PostDocument, GroupDocument, ChatDocument, PrivateMessageDocument, PhotoalbumDocument, \
    ImageDocument, UserDocument


def search_posts(request):
    q = request.GET.get('q')

    if q:
        posts = PostDocument.search().query('match', body=q)
    else:
        posts = ''
    return render(request, 'search_posts.html', {'posts': posts})


def search_groups(request):
    q = request.GET.get('q')

    if q:
        groups = GroupDocument.search().query('match', title=q)
    else:
        groups = ''
    return render(request, 'search_groups.html', {'groups': groups})


def search_chats(request):
    q = request.GET.get('q')

    if q:
        chats = ChatDocument.search().query('match', title=q)
    else:
        chats = ''
    return render(request, 'search_chats.html', {'chats': chats})


def search_private_messages(request):
    q = request.GET.get('q')

    if q:
        private_messages = PrivateMessageDocument.search().query('match', body=q)
    else:
        private_messages = ''
    return render(request, 'search_private_messages.html', {'private_messages': private_messages})


def search_photoalbums(request):
    q = request.GET.get('q')

    if q:
        photoalbums = PhotoalbumDocument.search().query('match', title=q)
    else:
        photoalbums = ''
    return render(request, 'search_photoalbums.html', {'photoalbums': photoalbums})


def search_images(request):
    q = request.GET.get('q')

    if q:
        images = ImageDocument.search().query('match', description=q)
    else:
        images = ''
    return render(request, 'search_images.html', {'images': images})


def search_users(request):
    q = request.GET.get('q')

    if q:
        users = UserDocument.search().query('match', name=q)
    else:
        users = ''
    return render(request, 'search_users.html', {'users': users})

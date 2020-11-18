from django.shortcuts import render, redirect
from search.documents import ChatDocument, PhotoalbumDocument, \
    ImageDocument, UserDocument, PostDocument, GroupDocument


def search_everything(request):
    title = 'Search Results'
    mq = request.GET.get('mq')
    searched_results = {}

    if request.method == 'GET':
        if mq:
            searched_users = UserDocument.search().query('match', name=mq)
            if searched_users:
                users = {'users': list(searched_users)}
                searched_results.update(users)

            searched_groups = GroupDocument.search().query('match', title=mq)
            if searched_groups:
                groups = {'groups': list(searched_groups)}
                searched_results.update(groups)

            searched_photoalbums = PhotoalbumDocument.search().query('match', title=mq)
            if searched_photoalbums:
                photoalbums = {'photoalbums': list(searched_photoalbums)}
                searched_results.update(photoalbums)

            searched_posts = PostDocument.search().query('match', body=mq)
            if searched_posts:
                posts = {'posts': list(searched_posts)}
                searched_results.update(posts)
            return render(request, 'searched_results.html', {'searched_results': searched_results,
                                                      'title': title})
        else:
            searched_results = {}
    return redirect(request.META.get('HTTP_REFERER', '/'))


def search_chats(request):
    q = request.GET.get('q')
    title = 'Search Chats'
    if q:
        chats = ChatDocument.search().query('match', title=q)
    else:
        chats = ''
    return render(request, 'search_chats.html', {'chats': chats, 'title': title})


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

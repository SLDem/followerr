from django.shortcuts import render
from search.documents import PostDocument


def search(request):
    q = request.GET.get('q')

    if q:
        posts = PostDocument.search().query('match', body=q)
    else:
        posts = ''
    return render(request, 'search_posts.html', {'posts': posts})

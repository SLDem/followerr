from django_elasticsearch_dsl import Document, Index, fields

from posts.models import Post
from user_profile.models import User
from groups.models import Group
from chats.models import Chat, Message
from photoalbums.models import Photoalbum, Image

posts = Index('posts')
groups = Index('groups')
chats = Index('chats')
photoalbums = Index('photoalbums')
images = Index('images')
users = Index('users')
messages = Index('messages')


@users.doc_type
class UserDocument(Document):
    image = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'image': fields.FileField()
    })

    class Index:
        name = 'users'

    class Django:
        model = User
        fields = [
            'id',
            'name',
            'following',
            'is_staff',
            'gender',
        ]


@photoalbums.doc_type
class ImageDocument(Document):
    album = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'title': fields.TextField(),
        'user': fields.ObjectField(properties={
            'id': fields.IntegerField(),
            'name': fields.ObjectField()
        })
    })

    class Index:
        name = 'images'

    class Django:
        model = Image
        fields = [
            'id',
            'description',
            'image'
        ]


@photoalbums.doc_type
class PhotoalbumDocument(Document):
    user = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField()
    })

    class Index:
        name = 'photoalbums'

    class Django:
        model = Photoalbum
        fields = [
            'id',
            'title',
            'created_at',
        ]



@chats.doc_type
class ChatDocument(Document):
    users = fields.NestedField(properties={
        'id': fields.IntegerField(),
        'image': fields.ObjectField(properties={
            'id': fields.IntegerField()
        }),
    })

    class Index:
        name = 'chats'

    class Django:
        model = Chat
        fields = [
            'id',
            'title',
            'image',
        ]


@posts.doc_type
class PostDocument(Document):
    user = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
        'gender': fields.BooleanField(),
        'is_staff': fields.BooleanField(),
        'image': fields.ObjectField(properties={
            'id': fields.IntegerField(),
            'image': fields.FileField(),
        })
    })

    group = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'title': fields.TextField(),
    })

    likers = fields.NestedField(properties={
        'id': fields.IntegerField(),
    })

    dislikers = fields.NestedField(properties={
        'id': fields.IntegerField(),
    })

    class Index:
        name = 'posts'

    class Django:
        model = Post
        fields = [
            'id',
            'body',
            'image',
            'date_posted'

        ]



@groups.doc_type
class GroupDocument(Document):
    users = fields.ObjectField(properties={
        'id': fields.IntegerField()
    })

    class Index:
        name = 'groups'

    class Django:
        model = Group
        fields = [
            'id',
            'title',
            'image',

        ]


@messages.doc_type
class MessageDocument(Document):
    chat = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'title': fields.TextField(),
        'owner': fields.ObjectField(properties={
            'id': fields.IntegerField(),
            'name': fields.TextField(),
            'image': fields.ObjectField(properties={
                'id': fields.IntegerField(),
                'image': fields.FileField()
            })
        })
    })

    from_user = fields.ObjectField(properties={
            'id': fields.IntegerField(),
            'name': fields.TextField(),
            'image': fields.ObjectField(properties={
                'id': fields.IntegerField(),
                'image': fields.FileField()
            })
        })

    class Index:
        name = 'messages'

    class Django:
        model = Message
        fields = [
            'id',
            'image',
            'body',
            'created_at',
            'is_read',
        ]
from django_elasticsearch_dsl import Document, Index, fields

from posts.models import Post
from user_profile.models import User
from groups.models import Group
from chats.models import Chat, PrivateMessage
from photoalbums.models import Photoalbum, Image

posts = Index('posts')
groups = Index('groups')
chats = Index('chats')
private_messages = Index('private_messages')
photoalbums = Index('photoalbums')
images = Index('images')
users = Index('users')


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
        related_models = [Image]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Image):
            return related_instance.image_set.all()


@photoalbums.doc_type
class ImageDocument(Document):
    class Index:
        name = 'images'

    class Django:
        model = Image
        fields = [
            'id',
            'description',
            'image'
        ]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, User):
            return related_instance.user_set.all()


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
        related_models = [User]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, User):
            return related_instance.user_set.all()


@private_messages.doc_type
class PrivateMessageDocument(Document):
    from_user = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
        'gender': fields.BooleanField(),
        'image': fields.ObjectField(properties={
            'id': fields.IntegerField(),
            'image': fields.FileField(),
        }),
    })

    to_user = fields.ObjectField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
        'gender': fields.BooleanField(),
        'image': fields.ObjectField(properties={
            'id': fields.IntegerField(),
            'image': fields.FileField(),
        }),
    })

    class Index:
        name = 'private_messages'

    class Django:
        model = PrivateMessage
        fields = [
            'id',
            'body',
            'created_at',
        ]
        related_models = [User]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, User):
            return related_instance.user_set.all()


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
        related_models = [User]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, User):
            return related_instance.user_set.all()


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
        related_models = [User, Group]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, User):
            return related_instance.user_set.all()


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
        related_models = [User]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, User):
            return related_instance.user_set.all()



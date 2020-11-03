from django_elasticsearch_dsl import Document, Index, fields
from posts.models import Post
from user_profile.models import User

posts = Index('posts')


@posts.doc_type
class PostDocument(Document):
    user = fields.NestedField(properties={
        'id': fields.IntegerField(),
        'name': fields.TextField(),
        'gender': fields.BooleanField(),
        'is_staff': fields.BooleanField(),
    })

    group = fields.NestedField(properties={
        'id': fields.IntegerField(),
        'title': fields.TextField(),
    })

    class Index:
        name = 'posts'

    class Django:
        model = Post
        fields = [
            'id',
            'body',
        ]
        related_models = [User]

    def get_instances_from_related(self, tag_instance):
        return tag_instance.post_set.all()


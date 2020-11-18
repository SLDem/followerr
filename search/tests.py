from django.test import TestCase, Client
from django.utils.encoding import force_bytes
from django.core.files.uploadedfile import SimpleUploadedFile

from .documents import UserDocument, ImageDocument, PhotoalbumDocument, ChatDocument, \
    PostDocument, GroupDocument

from posts.models import Post
from groups.models import Group
from chats.models import Chat
from photoalbums.models import Image, Photoalbum
from user_profile.models import User


from django_elasticsearch_dsl.documents import DocType

from .documents import posts, groups, chats, photoalbums, images, users
import os

from Followerr.settings import MEDIA_ROOT
SEARCH_DIR = os.path.dirname(os.path.abspath(__file__))
search_image_path = os.path.join(SEARCH_DIR, 'test.jpg')


class DocTypeUserTestCase(TestCase):
    def test_model_class_added(self):
        self.assertEqual(UserDocument.django.model, User)

    def test_ignore_signals_default(self):
        self.assertFalse(UserDocument.django.ignore_signals)

    def test_auto_refresh_default(self):
        self.assertTrue(UserDocument.django.auto_refresh)

    def test_ignore_signals_added(self):
        @users.doc_type
        class UserDocument2(DocType):

            class Index:
                name = 'users'

            class Django:
                model = User
                ignore_signals = True

        self.assertTrue(UserDocument2.django.ignore_signals)


class DocTypeImageTestCase(TestCase):
    def test_model_class_added(self):
        self.assertEqual(ImageDocument.django.model, Image)

    def test_ignore_signals_default(self):
        self.assertFalse(ImageDocument.django.ignore_signals)

    def test_auto_refresh_default(self):
        self.assertTrue(ImageDocument.django.auto_refresh)

    def test_ignore_signals_added(self):
        @images.doc_type
        class ImageDocument2(DocType):

            class Index:
                name = 'images'

            class Django:
                model = Image
                ignore_signals = True

        self.assertTrue(ImageDocument2.django.ignore_signals)


class DocTypePhotoalbumTestCase(TestCase):
    def test_model_class_added(self):
        self.assertEqual(PhotoalbumDocument.django.model, Photoalbum)

    def test_ignore_signals_default(self):
        self.assertFalse(PhotoalbumDocument.django.ignore_signals)

    def test_auto_refresh_default(self):
        self.assertTrue(PhotoalbumDocument.django.auto_refresh)

    def test_ignore_signals_added(self):
        @photoalbums.doc_type
        class PhotoalbumDocument2(DocType):

            class Index:
                name = 'photoalbums'

            class Django:
                model = Photoalbum
                ignore_signals = True

        self.assertTrue(PhotoalbumDocument2.django.ignore_signals)


class DocTypePrivateMessageTestCase(TestCase):
    def test_model_class_added(self):
        self.assertEqual(PrivateMessageDocument.django.model, PrivateMessage)

    def test_ignore_signals_default(self):
        self.assertFalse(PrivateMessageDocument.django.ignore_signals)

    def test_auto_refresh_default(self):
        self.assertTrue(PrivateMessageDocument.django.auto_refresh)

    def test_ignore_signals_added(self):
        @private_messages.doc_type
        class PrivateMessageDocument2(DocType):

            class Index:
                name = 'photoalbums'

            class Django:
                model = PrivateMessage
                ignore_signals = True

        self.assertTrue(PrivateMessageDocument2.django.ignore_signals)


class DocTypeChatTestCase(TestCase):
    def test_model_class_added(self):
        self.assertEqual(ChatDocument.django.model, Chat)

    def test_ignore_signals_default(self):
        self.assertFalse(ChatDocument.django.ignore_signals)

    def test_auto_refresh_default(self):
        self.assertTrue(ChatDocument.django.auto_refresh)

    def test_ignore_signals_added(self):
        @chats.doc_type
        class ChatDocument2(DocType):

            class Index:
                name = 'chats'

            class Django:
                model = Chat
                ignore_signals = True

        self.assertTrue(ChatDocument2.django.ignore_signals)

class DocTypePostTestCase(TestCase):
    def test_model_class_added(self):
        self.assertEqual(PostDocument.django.model, Post)

    def test_ignore_signals_default(self):
        self.assertFalse(PostDocument.django.ignore_signals)

    def test_auto_refresh_default(self):
        self.assertTrue(PostDocument.django.auto_refresh)

    def test_ignore_signals_added(self):
        @posts.doc_type
        class PostDocument2(DocType):

            class Index:
                name = 'posts'

            class Django:
                model = Post
                ignore_signals = True

        self.assertTrue(PostDocument2.django.ignore_signals)


class DocTypeGroupTestCase(TestCase):
    def test_model_class_added(self):
        self.assertEqual(GroupDocument.django.model, Group)

    def test_ignore_signals_default(self):
        self.assertFalse(GroupDocument.django.ignore_signals)

    def test_auto_refresh_default(self):
        self.assertTrue(GroupDocument.django.auto_refresh)

    def test_ignore_signals_added(self):
        @groups.doc_type
        class GroupDocument2(DocType):

            class Index:
                name = 'groups'

            class Django:
                model = Group
                ignore_signals = True

        self.assertTrue(GroupDocument2.django.ignore_signals)


class SearchViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(name='test', email='test@gmail.com', password='test')
        self.user1 = User.objects.create_user(name='test1', email='test1@gmail.com', password='test1')
        self.client.force_login(self.user)
        self.photoalbum = Photoalbum.objects.create(title='test_album2', user=self.user)
        self.image = SimpleUploadedFile(name='test_image.jpg',
                                        content=open(search_image_path, 'rb').read(),
                                        content_type='image/jpg')

    def test_chats_search(self):
        Chat.objects.create(title='Chat 1', owner=self.user)
        Chat.objects.create(title='Chat 2', owner=self.user)
        response = self.client.get('/search_chats/?q=Chat', follow=True)
        self.assertIn(force_bytes('Chat 1'), response.content)
        self.assertIn(force_bytes('Chat 2'), response.content)

    def test_chats_search_fail(self):
        Chat.objects.create(title='Chat', owner=self.user)
        Chat.objects.create(title='Cha', owner=self.user)
        response = self.client.get('/search_chats/?q=Ch', follow=True)
        self.assertNotIn(force_bytes('Chat'), response.content)
        self.assertNotIn(force_bytes('Cha'), response.content)

    def test_chats_search_empty(self):
        response = self.client.get('/search_chats/?q=', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_private_message_search(self):
        PrivateMessage.objects.create(from_user=self.user, to_user=self.user1, body='test_msg')
        PrivateMessage.objects.create(from_user=self.user1, to_user=self.user, body='test_msg 2')
        response = self.client.get('/search_private_messages/?q=test_msg', follow=True)
        self.assertIn(force_bytes('test_msg'), response.content)
        self.assertIn(force_bytes('test_msg 2'), response.content)

    def test_private_message_search_fail(self):
        PrivateMessage.objects.create(from_user=self.user, to_user=self.user1, body='test_ms')
        PrivateMessage.objects.create(from_user=self.user1, to_user=self.user, body='test_m')
        response = self.client.get('/search_private_messages/?q=test_msg', follow=True)
        self.assertNotIn(force_bytes('test_ms'), response.content)
        self.assertNotIn(force_bytes('test_m'), response.content)

    def test_private_message_search_empty(self):
        response = self.client.get('/search_private_messages/?q=', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_search_photoalbums(self):
        Photoalbum.objects.create(title='test_album', user=self.user)
        Photoalbum.objects.create(title='test_album 1', user=self.user)
        response = self.client.get('/search_photoalbums/?q=test_album', follow=True)
        self.assertIn(force_bytes('test_album'), response.content)
        self.assertIn(force_bytes('test_album 1'), response.content)

    def test_search_photoalbums_fail(self):
        Photoalbum.objects.create(title='test_albu', user=self.user)
        Photoalbum.objects.create(title='test_alb', user=self.user)
        response = self.client.get('/search_photoalbums/?q=test_a', follow=True)
        self.assertNotIn(force_bytes('test_albu'), response.content)
        self.assertNotIn(force_bytes('test_alb'), response.content)

    def test_photoalbums_search_empty(self):
        response = self.client.get('/search_photoalbums/?q=', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_search_images(self):
        Image.objects.create(description='test_image 1', album=self.photoalbum,
                             image=SimpleUploadedFile(name='test_image1.jpg', content=open(search_image_path, 'rb').read(),
                                                      content_type='image/jpg'))
        Image.objects.create(description='test_image 2', album=self.photoalbum,
                             image=SimpleUploadedFile(name='test_image2.jpg', content=open(search_image_path, 'rb').read(),
                                                      content_type='image/jpg'))
        response = self.client.get('/search_images/?q=test_image', follow=True)
        self.assertIn(force_bytes('test_image'), response.content)
        self.assertIn(force_bytes('test_image'), response.content)
        os.remove(MEDIA_ROOT + 'images/test_image1.jpg')
        os.remove(MEDIA_ROOT + 'images/test_image2.jpg')

    def test_search_images_fail(self):
        Image.objects.create(description='test_image 1', album=self.photoalbum,
                             image=SimpleUploadedFile(name='test_image1.jpg', content=open(search_image_path, 'rb').read(),
                                                      content_type='image/jpg'))
        Image.objects.create(description='test_image 2', album=self.photoalbum,
                             image=SimpleUploadedFile(name='test_image2.jpg', content=open(search_image_path, 'rb').read(),
                                                      content_type='image/jpg'))
        response = self.client.get('/search_images/?q=test_ge', follow=True)
        self.assertNotIn(force_bytes('test_image 1'), response.content)
        self.assertNotIn(force_bytes('test_image 2'), response.content)
        os.remove(MEDIA_ROOT + 'images/test_image1.jpg')
        os.remove(MEDIA_ROOT + 'images/test_image2.jpg')

    def test_images_search_empty(self):
        response = self.client.get('/search_images/?q=', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_search_users(self):
        response = self.client.get('/search_users/?q=test', follow=True)
        self.assertIn(force_bytes('test'), response.content)

    def test_search_users_fail(self):
        response = self.client.get('/search_users/?q=tes', follow=True)
        self.assertNotIn(force_bytes('test'), response.content)

    def test_users_search_empty(self):
        response = self.client.get('/search_users/?q=', follow=True)
        self.assertEqual(response.status_code, 200)
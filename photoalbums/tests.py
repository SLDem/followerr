from django.test import TestCase, Client, tag
from django.utils.encoding import force_bytes
from django.urls import reverse

from django.db.utils import IntegrityError

from .models import Photoalbum, Image
from .forms import NewPhotoalbumForm, NewImageForm

from comments.forms import NewCommentForm
from comments.models import Comment
from user_profile.models import User

from Followerr.settings import MEDIA_ROOT

from django.core.files.uploadedfile import SimpleUploadedFile

import os

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
test_image_path = os.path.join(TEST_DIR, 'test.jpg')


class PhotoalbumsModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(name='test', email='test@gmail.com', password='test')
        self.photoalbum = Photoalbum.objects.create(title='test_album', user=self.user)
        self.image = Image.objects.create(description='test_image', album=self.photoalbum)

    def test_photoalbum_creation(self):
        Photoalbum.objects.create(title='test_album1', user=self.user)
        self.assertEqual(len(Photoalbum.objects.filter(title='test_album1', user=self.user)), 1)

    def test_photoalbum_deletion(self):
        self.photoalbum.delete()
        self.assertEqual(len(Photoalbum.objects.filter(title='test_album', user=self.user)), 0)

    def test_image_creation(self):
        Image.objects.create(description='test_image1', album=self.photoalbum,
                             image=SimpleUploadedFile(name='test_image.jpg', content=open(test_image_path, 'rb').read(),
                                                      content_type='image/jpg'))
        self.assertEqual(len(Image.objects.filter(description='test_image1', album=self.photoalbum)), 1)

    def test_image_deletion(self):
        self.image.delete()
        self.assertEqual(len(Image.objects.filter(description='test_image', album=self.photoalbum)), 0)


class PhotoalbumViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(name='test', email='test@gmail.com', password='test')
        self.user1 = User.objects.create_user(name='test1', email='test1@gmail.com', password='test1')
        self.client.force_login(self.user)

        self.photoalbum = Photoalbum.objects.create(title='test_album', user=self.user)
        self.photoalbum1 = Photoalbum.objects.create(title='test_album1', user=self.user1)

        self.image = SimpleUploadedFile(name='test_image.jpg',
                                        content=open(test_image_path, 'rb').read(),
                                        content_type='image/jpg')

    def post_image(self):
        data = {'description': 'test_image1', 'image': self.image}
        self.client.post(reverse('photoalbum', kwargs={'pk': self.photoalbum.pk}), data=data)
        image = Image.objects.get(description='test_image1')
        return image

    def test_photoalbums_view(self):
        response = self.client.get(reverse('photoalbums', kwargs={'pk': self.user.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'photoalbums.html')

    def test_photoalbums_view_fail(self):
        response = self.client.get(reverse('photoalbums', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('User does not exist'), response.content)

    def test_photoalbums_new_album(self):
        data = {'title': 'test_photoalbum1'}
        self.client.post(reverse('photoalbums', kwargs={'pk': self.user.pk}), data=data, follow=True)
        self.assertTrue(isinstance(Photoalbum.objects.get(title='test_photoalbum1'), Photoalbum))

    def test_photoalbums_new_album_not_owner(self):
        self.client.logout()
        self.client.force_login(self.user1)
        data = {'title': 'test_photoalbum1'}
        response = self.client.post(reverse('photoalbums', kwargs={'pk': self.user.pk}), data=data, follow=True)
        self.assertIn(force_bytes('Action not allowed'), response.content)

    def test_photoalbum_view(self):
        response = self.client.get(reverse('photoalbum', kwargs={'pk': self.photoalbum.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'photoalbum.html')

    def test_photoalbum_view_fail(self):
        response = self.client.get(reverse('photoalbum', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('Photoalbum does not exist'), response.content)

    def test_photoalbum_new_image(self):
        data = {'description': 'test_image1', 'image': self.image}
        self.client.post(reverse('photoalbum', kwargs={'pk': self.photoalbum.pk}), data=data)
        self.assertTrue(isinstance(Image.objects.get(description='test_image1'), Image))
        os.remove(MEDIA_ROOT + 'images/test_image.jpg')

    def test_photoalbum_new_image_not_album_owner(self):
        data = {'description': 'test_image1', 'image': self.image}
        response = self.client.post(reverse('photoalbum', kwargs={'pk': self.photoalbum1.pk}), data=data)
        self.assertIn(force_bytes('Action not allowed'), response.content)

    def test_image_detail_view(self):
        image = self.post_image()
        response = self.client.get(reverse('image_detail', kwargs={'pk': image.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'image_detail.html')
        os.remove(MEDIA_ROOT + 'images/test_image.jpg')

    def test_image_detail_view_fail(self):
        response = self.client.get(reverse('image_detail', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('Image does not exist'), response.content)

    def test_image_detail_view_post_comment(self):
        image = self.post_image()
        data = {'body': 'test_comment'}
        self.client.post(reverse('image_detail', kwargs={'pk': image.pk}), data=data)
        self.assertTrue(len(Comment.objects.filter(body='test_comment', picture=image)), 1)
        os.remove(MEDIA_ROOT + 'images/test_image.jpg')

    def test_make_avatar(self):
        image = self.post_image()
        self.client.get(reverse('make_avatar', kwargs={'pk': image.pk}), follow=True)
        self.user.refresh_from_db()
        self.assertEqual(self.user.image, image)
        os.remove(MEDIA_ROOT + 'images/test_image.jpg')

    def test_make_avatar_not_image_owner(self):
        image = self.post_image()
        self.client.logout()
        self.client.force_login(self.user1)
        response = self.client.get(reverse('make_avatar', kwargs={'pk': image.pk}), follow=True)
        self.assertIn(force_bytes('Action not allowed'), response.content)
        os.remove(MEDIA_ROOT + 'images/test_image.jpg')

    def test_make_avatar_no_image(self):
        response = self.client.get(reverse('make_avatar', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('Image does not exist'), response.content)

    def test_reply_form_picture_get(self):
        image = self.post_image()
        comment = Comment.objects.create(picture=image, user=self.user, body='test_comment')
        data = {'body': 'test comment with parent',
                'parent_id': comment.pk}
        response = self.client.get(reverse('reply_form_picture', kwargs={'pk': image.pk, 'parent_id': comment.pk}), data=data)
        self.assertEqual(response.status_code, 200)
        os.remove(MEDIA_ROOT + 'images/test_image.jpg')

    def test_reply_form_picture(self):
        image = self.post_image()
        comment = Comment.objects.create(picture=image, user=self.user, body='test_comment')
        data = {'body': 'test comment with parent',
                'parent_id': comment.pk}
        self.client.post(reverse('reply_form_picture', kwargs={'pk': image.pk, 'parent_id': comment.pk}), data=data)
        self.assertTrue(isinstance(Comment.objects.filter(body='test comment with parent').first(), Comment))
        os.remove(MEDIA_ROOT + 'images/test_image.jpg')

    def test_reply_form_picture_no_parent(self):
        image = self.post_image()
        comment = Comment.objects.create(picture=image, user=self.user, body='test_comment')
        data = {'body': 'test comment with parent'}
        self.client.post(reverse('reply_form_picture', kwargs={'pk': image.pk, 'parent_id': comment.pk}),
                         data=data,
                         follow=True)
        self.assertTrue(isinstance(Comment.objects.filter(body='test comment with parent').first(), Comment))
        os.remove(MEDIA_ROOT + 'images/test_image.jpg')

    def test_reply_form_picture_fail(self):
        image = self.post_image()
        comment = Comment.objects.create(picture=image, user=self.user, body='test_comment')
        data = {'body': 'test comment with parent'}
        response = self.client.post(reverse('reply_form_picture', kwargs={'pk': '10', 'parent_id': comment.pk}),
                                    data=data,
                                    follow=True)
        self.assertIn(force_bytes('Image does not exist'), response.content)
        os.remove(MEDIA_ROOT + 'images/test_image.jpg')

    def test_edit_image(self):
        image = self.post_image()
        data = {'description': 'test_desc'}
        self.client.post(reverse('edit_image', kwargs={'pk': image.pk}), data=data)
        response = self.client.get(reverse('edit_image', kwargs={'pk': image.pk}), follow=True)
        img = Image.objects.get(description='test_desc')
        self.assertTrue(isinstance(img, Image))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_image.html')
        os.remove(MEDIA_ROOT + 'images/test_image.jpg')

    def test_edit_image_fail(self):
        data = {'description': 'test_desc'}
        response = self.client.post(reverse('edit_image', kwargs={'pk': '10'}), data=data)
        self.assertEqual(len(Image.objects.filter(description='test_desc')), 0)
        self.assertIn(force_bytes('Image does not exist'), response.content)

    def test_edit_image_not_owner(self):
        image = self.post_image()
        self.client.logout()
        self.client.force_login(self.user1)
        data = {'description': 'test_desc'}
        response = self.client.post(reverse('edit_image', kwargs={'pk': image.pk}), data=data)
        self.assertIn(force_bytes('Action not allowed'), response.content)
        os.remove(MEDIA_ROOT + 'images/test_image.jpg')

    def test_delete_image(self):
        image = self.post_image()
        self.client.get(reverse('delete_image', kwargs={'pk': image.pk}), follow=True)
        self.assertEqual(len(Image.objects.filter(description='test_image1')), 0)
        os.remove(MEDIA_ROOT + 'images/test_image.jpg')

    @tag('fast')
    def test_delete_image_avatar(self):
        image = self.post_image()
        self.user.image = image
        self.user.save()
        self.client.get(reverse('delete_image', kwargs={'pk': image.pk}), follow=True)
        self.assertEqual(len(Image.objects.filter(description='test_image1')), 0)
        self.user.refresh_from_db()
        os.remove(MEDIA_ROOT + 'images/test_image.jpg')

    def test_delete_image_fail(self):
        response = self.client.get(reverse('delete_image', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('Image does not exist'), response.content)

    def test_delete_image_not_owner(self):
        image = self.post_image()
        self.client.logout()
        self.client.force_login(self.user1)
        response = self.client.get(reverse('delete_image', kwargs={'pk': image.pk}), follow=True)
        self.assertIn(force_bytes('Action not allowed'), response.content)
        os.remove(MEDIA_ROOT + 'images/test_image.jpg')

    def test_edit_photoalbum_view(self):
        response = self.client.get(reverse('edit_album', kwargs={'pk': self.photoalbum.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_photoalbum.html')

    def test_edit_photoalbum(self):
        data = {'title': 'changed_title'}
        self.client.post(reverse('edit_album', kwargs={'pk': self.photoalbum.pk}), data=data)
        self.assertEqual(len(Photoalbum.objects.filter(title='changed_title')), 1)

    def test_edit_photoalbum_not_owner(self):
        self.client.logout()
        self.client.force_login(self.user1)
        data = {'title': 'changed_title'}
        response = self.client.post(reverse('edit_album', kwargs={'pk': self.photoalbum.pk}), data=data)
        self.assertIn(force_bytes('Action not allowed'), response.content)

    def test_edit_photoalbum_no_album(self):
        data = {'title': 'changed_title'}
        response = self.client.post(reverse('edit_album', kwargs={'pk': '10'}), data=data)
        self.assertIn(force_bytes('Photoalbum does not exist'), response.content)

    def test_delete_photoalbum(self):
        self.client.get(reverse('delete_album', kwargs={'pk': self.photoalbum.pk}), follow=True)
        self.assertEqual(len(Photoalbum.objects.filter(title='test_album')), 0)

    def test_delete_photoalbum_not_owner(self):
        self.client.logout()
        self.client.force_login(self.user1)
        response = self.client.get(reverse('delete_album', kwargs={'pk': self.photoalbum.pk}), follow=True)
        self.assertIn(force_bytes('Action not allowed'), response.content)

    def test_delete_photoalbum_no_album(self):
        response = self.client.get(reverse('delete_album', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('Photoalbum does not exist'), response.content)

    def test_like_image(self):
        self.image = self.post_image()
        self.client.get(reverse('like_image', kwargs={'pk': self.image.pk}))
        self.assertIn(self.user, self.image.likers.all())

        self.client.get(reverse('like_image', kwargs={'pk': self.image.pk}))
        self.assertNotIn(self.user, self.image.likers.all())
        self.assertNotIn(self.user, self.image.dislikers.all())

        self.client.get(reverse('like_image', kwargs={'pk': self.image.pk}))
        self.assertIn(self.user, self.image.likers.all())
        self.assertNotIn(self.user, self.image.dislikers.all())

        self.image.dislikers.add(self.user)
        self.image.likers.remove(self.user)
        self.client.get(reverse('like_image', kwargs={'pk': self.image.pk}))
        self.assertIn(self.user, self.image.likers.all())
        self.assertNotIn(self.user, self.image.dislikers.all())
        os.remove(MEDIA_ROOT + 'images/test_image.jpg')

    def test_like_image_fail(self):
        response = self.client.get(reverse('like_image', kwargs={'pk': '10'}))
        self.assertIn(force_bytes('Image does not exist'), response.content)

    def test_dislike_image(self):
        self.image = self.post_image()
        self.client.get(reverse('dislike_image', kwargs={'pk': self.image.pk}))
        self.assertIn(self.user, self.image.dislikers.all())

        self.client.get(reverse('dislike_image', kwargs={'pk': self.image.pk}))
        self.assertNotIn(self.user, self.image.dislikers.all())
        self.assertNotIn(self.user, self.image.likers.all())

        self.client.get(reverse('dislike_image', kwargs={'pk': self.image.pk}))
        self.assertIn(self.user, self.image.dislikers.all())
        self.assertNotIn(self.user, self.image.likers.all())

        self.image.likers.add(self.user)
        self.image.dislikers.remove(self.user)
        self.client.get(reverse('dislike_image', kwargs={'pk': self.image.pk}))
        self.assertIn(self.user, self.image.dislikers.all())
        self.assertNotIn(self.user, self.image.likers.all())
        os.remove(MEDIA_ROOT + 'images/test_image.jpg')

    def test_dislike_image_fail(self):
        response = self.client.get(reverse('dislike_image', kwargs={'pk': '10'}))
        self.assertIn(force_bytes('Image does not exist'), response.content)


class PhotoalbumFormTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(name='test', email='test@gmail.com', password='test')
        self.client.force_login(self.user)
        self.photoalbum = Photoalbum.objects.create(title='test_album', user=self.user)
        self.image = SimpleUploadedFile(name='test_image.jpg', content=open(test_image_path, 'rb').read(),
                                        content_type='image/jpg')

    def test_new_photoalbum_form_valid(self):
        data = {'title': 'test_album'}
        form = NewPhotoalbumForm(data=data)
        self.assertTrue(form.is_valid())

    def test_new_photoalbum_form_invalid(self):
        data = {'title': ''}
        form = NewPhotoalbumForm(data=data)
        self.assertFalse(form.is_valid())

    def test_new_image_form_valid(self):
        data = {'description': 'test_image', 'album': self.photoalbum}
        form = NewImageForm(data=data, files={'image': self.image})
        self.assertTrue(form.is_valid())

    def test_new_image_form_invalid_no_description(self):
        data = {'description': '', 'album': self.photoalbum}
        form = NewImageForm(data=data, files={'image': self.image})
        self.assertFalse(form.is_valid())

    def test_new_image_form_invalid_no_album(self):
        data = {'description': 'test_image', 'album': '15'}
        form = NewImageForm(data=data, files={'image': self.image})
        with self.assertRaises(Exception) as raised:
            form.save()
        self.assertEqual(IntegrityError, type(raised.exception))

    def test_new_image_form_invalid_no_image(self):
        data = {'description': 'test_image', 'album': self.photoalbum}
        form = NewImageForm(data=data)
        self.assertFalse(form.is_valid())

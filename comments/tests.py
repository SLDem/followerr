from django.test import TestCase, Client
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.utils import timezone
from django.core import mail

from .forms import NewCommentForm

from online_users.models import OnlineUserActivity
from posts.models import Post
from user_profile.models import User

from .models import Comment

from django.utils.http import urlsafe_base64_encode

from django.test import tag


class CommentsModelTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@gmail.com', password='test', name='test')
        self.post = Post.objects.create(user=self.user, body='test_post')
        self.comment = Comment.objects.create(post=self.post, user=self.user, body='test_comment')

    def test_comment_creation(self):
        comment = Comment.objects.create(post=self.post, user=self.user, body='test_comment1')
        self.assertTrue(isinstance(comment, Comment))

    def test_comment_deletion(self):
        self.comment.delete()
        self.assertEqual(len(Comment.objects.filter(body='test_comment')), 0)


class CommentsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@gmail.com', password='test', name='test')
        self.user1 = User.objects.create_user(name='test1', email='test1@gmail.com', password='test1')
        self.post = Post.objects.create(user=self.user, body='test_post')
        self.comment = Comment.objects.create(post=self.post, user=self.user, body='test_comment')
        self.client.force_login(self.user)

    def test_reply_form_with_parent(self):
        data = {'body': 'test comment with parent',
                'parent_id': self.comment.pk}
        response = self.client.post(reverse('reply_form', kwargs={'pk': self.post.pk, 'parent_id': self.comment.pk}),
                                    data=data, follow=True)
        self.assertTrue(isinstance(Comment.objects.filter(body='test comment with parent').first(), Comment))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'post_detail.html')

    def test_reply_form_with_no_parent(self):
        data = {'body': 'test comment with parent'}
        self.client.post(reverse('reply_form', kwargs={'pk': self.post.pk, 'parent_id': self.comment.pk}),
                                    data=data, follow=True)
        self.assertTrue(isinstance(Comment.objects.filter(body='test comment with parent').first(), Comment))

    def test_reply_form_with_parent_fail_no_post(self):
        data = {'body': 'test comment with parent',
                'parent_id': self.comment.pk}
        response = self.client.post(reverse('reply_form', kwargs={'pk': '10', 'parent_id': self.comment.pk}),
                                    data=data, follow=True)
        self.assertIn(force_bytes('Action not allowed'), response.content)

    def test_reply_form_not_user(self):
        self.client.logout()
        response = self.client.get(reverse('post_detail', kwargs={'pk': self.post.pk}), follow=True)
        self.assertRedirects(response, '/login/')

    def test_delete_comment(self):
        self.client.get(reverse('delete_comment', kwargs={'pk': self.comment.pk}), follow=True)
        self.assertEqual(len(Comment.objects.filter(body='test_comment')), 0)

    def test_delete_comment_not_commenter(self):
        comment = Comment.objects.create(user=self.user1, body='test_comment1')
        response = self.client.get(reverse('delete_comment', kwargs={'pk': comment.pk}), follow=True)
        self.assertIn(force_bytes('You can only delete your own comments'), response.content)

    def test_delete_comment_fail(self):
        response = self.client.get(reverse('delete_comment', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('Action not allowed'), response.content)

    def test_edit_comment(self):
        data = {'body': 'test comment changed'}
        self.client.post(reverse('edit_comment', kwargs={'pk': self.comment.pk}), data=data, follow=True)
        g_response = self.client.get(reverse('edit_comment', kwargs={'pk': self.comment.pk}), follow=True)
        self.assertIsNotNone(Comment.objects.filter(body='test comment changed'))
        self.assertTemplateUsed(g_response, 'edit_comment.html')

    def test_edit_comment_fail(self):
        data = {'body': 'test comment changed'}
        response = self.client.post(reverse('edit_comment', kwargs={'pk': '10'}), data=data, follow=True)
        self.assertIn(force_bytes('Action not allowed'), response.content)

    def test_like_comment(self):
        self.client.get(reverse('like_comment', kwargs={'pk': self.comment.pk}))
        self.assertIn(self.user, self.comment.likers.all())

        self.client.get(reverse('like_comment', kwargs={'pk': self.comment.pk}))
        self.assertNotIn(self.user, self.comment.likers.all())
        self.assertNotIn(self.user, self.comment.dislikers.all())

        self.client.get(reverse('like_comment', kwargs={'pk': self.comment.pk}))
        self.assertIn(self.user, self.comment.likers.all())
        self.assertNotIn(self.user, self.comment.dislikers.all())

        self.comment.dislikers.add(self.user)
        self.comment.likers.remove(self.user)
        self.client.get(reverse('like_comment', kwargs={'pk': self.comment.pk}))
        self.assertIn(self.user, self.comment.likers.all())
        self.assertNotIn(self.user, self.comment.dislikers.all())

    def test_like_comment_fail(self):
        response = self.client.get(reverse('like_comment', kwargs={'pk': '10'}))
        self.assertIn(force_bytes('Action not allowed'), response.content)

    def test_dislike_comment(self):
        self.client.get(reverse('dislike_comment', kwargs={'pk': self.comment.pk}))
        self.assertIn(self.user, self.comment.dislikers.all())

        self.client.get(reverse('dislike_comment', kwargs={'pk': self.comment.pk}))
        self.assertNotIn(self.user, self.comment.dislikers.all())
        self.assertNotIn(self.user, self.comment.likers.all())

        self.client.get(reverse('dislike_comment', kwargs={'pk': self.comment.pk}))
        self.assertIn(self.user, self.comment.dislikers.all())
        self.assertNotIn(self.user, self.comment.likers.all())

        self.comment.likers.add(self.user)
        self.comment.dislikers.remove(self.user)
        self.client.get(reverse('dislike_comment', kwargs={'pk': self.comment.pk}))
        self.assertIn(self.user, self.comment.dislikers.all())
        self.assertNotIn(self.user, self.comment.likers.all())

    def test_dislike_comment_fail(self):
        response = self.client.get(reverse('dislike_comment', kwargs={'pk': '10'}))
        self.assertIn(force_bytes('Action not allowed'), response.content)


class CommentsFormTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@gmail.com', password='test', name='test')
        self.post = Post.objects.create(user=self.user, body='test_post')
        self.comment = Comment.objects.create(post=self.post, user=self.user, body='test_comment')

    def test_new_comment_form_no_parent(self):
        data = {'body': 'test', 'post': self.post, 'user': self.user}
        form = NewCommentForm(data=data)
        self.assertTrue(form.is_valid())

    def test_new_comment_form_with_parent(self):
        data = {'body': 'test', 'post': self.post, 'user': self.user, 'parent': self.comment}
        form = NewCommentForm(data=data)
        self.assertTrue(form.is_valid())

    def test_new_comment_form_invalid(self):
        data = {'body': '', 'post': self.post, 'user': self.user}
        form = NewCommentForm(data=data)
        self.assertFalse(form.is_valid())

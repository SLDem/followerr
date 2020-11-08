from django.test import TestCase, Client
from django.utils.encoding import force_bytes, force_text
from django.urls import reverse

from .forms import NewPostForm

from .models import Post
from user_profile.models import User

from django.test import tag


class PostModelTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(email='test@gmail.com', password='test', name='test')
        Post.objects.create(user=user, body='hi')
        self.post = Post.objects.get(body='hi')
        self.user = User.objects.get(email='test@gmail.com')
        self.client.login(email=user.email, password=user.password)

    def test_post_creation(self):
        self.assertTrue(isinstance(self.post, Post))
        self.assertEqual(self.post.__unicode__(), self.post.body)

    def test_like_post(self):
        self.post.likers.add(self.user)
        if self.user in self.post.likers.all():
            self.post.likers.remove(self.user)
            self.assertNotIn(self.user, self.post.likers.all())
        elif self.user not in self.post.likers.all() and self.user in self.post.dislikers.all():
            self.post.likers.add(self.user)
            self.post.dislikers.remove(self.user)
            self.assertIn(self.user, self.post.likers.all())
        else:
            self.post.likers.add(self.user)
            self.assertIn(self.user, self.post.likers.all())

    def test_dislike_post(self):
        self.post.dislikers.add(self.user)
        if self.user in self.post.dislikers.all():
            self.post.dislikers.remove(self.user)
            self.assertNotIn(self.user, self.post.dislikers.all())
        elif self.user not in self.post.dislikers.all() and self.user in self.post.likers.all():
            self.post.dislikers.add(self.user)
            self.post.likers.remove(self.user)
            self.assertIn(self.user, self.post.dislikers.all())
        else:
            self.post.dislikers.add(self.user)
            self.assertIn(self.user, self.post.dislikers.all())

    def test_delete_post(self):
        post_to_delete = Post.objects.create(user=self.user, body='delete me')
        original_length = Post.objects.all().count()
        if self.user == post_to_delete.user:
            Post.objects.filter(body='delete me').delete()
            length_after_delete = Post.objects.all().count()
            self.assertIsNot(length_after_delete, original_length)


class PostViewTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(email='test@gmail.com', password='test', name='test')
        Post.objects.create(user=user, body='hi')
        self.post = Post.objects.get(body='hi')
        self.user = User.objects.get(email='test@gmail.com')
        self.client.login(email=user.email, password=user.password)

    def test_index(self):
        client = Client()
        get_response = client.get('/home/', {}, True)
        post_response = client.post(reverse('index'), data={'body': 'Test'}, follow=True)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(post_response.status_code, 200)

    def test_post_detail(self):
        client = Client()
        response = client.get('/post_detail/{0}/'.format(self.post.pk), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(force_bytes(self.post.body), response.content)

    def test_post_edit(self):
        client = Client()
        if self.post.user == self.user:
            response = client.get('/edit_post/{0}/'.format(self.post.pk), follow=True)
            self.assertEqual(response.status_code, 200)
        else:
            response = client.get('/edit_post/{0}/'.format(self.post.pk), follow=True)
            self.assertEqual(force_text(response.content), 'Action not allowed')


class AnonymousPostViewTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(email='test@gmail.com', password='test', name='test')
        Post.objects.create(user=user, body='hi')
        self.post = Post.objects.get(body='hi')
        self.user = User.objects.get(email='test@gmail.com')

    def test_index(self):
        client = Client()
        get_response = client.get('/home/', {}, True)
        post_response = client.post(reverse('index'), data={}, follow=True)
        self.assertRedirects(get_response, '/login/')
        self.assertRedirects(post_response, '/login/')

    def test_post_detail(self):
        client = Client()
        response = client.get('/post_detail/{0}/'.format(self.post.pk), follow=True)
        self.assertRedirects(response, '/login/')

    def test_post_edit(self):
        client = Client()
        response = client.get('/edit_post/{0}/'.format(self.post.pk))
        self.assertRedirects(response, '/login/')


class PostFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@gmail.com', password='test')

    def test_new_post_form_valid(self):
        p = Post.objects.create(user=self.user, body='hi')
        data = {'body': p.body}
        form = NewPostForm(data=data)
        self.assertTrue(form.is_valid())

    def test_new_post_form_invalid(self):
        p = Post.objects.create(user=self.user, body='')
        data = {'body': p.body}
        form = NewPostForm(data=data)
        self.assertFalse(form.is_valid())

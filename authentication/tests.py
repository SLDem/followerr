from django.test import TestCase, Client
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.utils import timezone
from django.core import mail

from .forms import SignupForm

from online_users.models import OnlineUserActivity
from user_profile.models import User

from django.utils.http import urlsafe_base64_encode

from django.test import tag


class AuthenticationViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@gmail.com', password='test', name='test')

    def test_see_online_users(self):
        self.time = timezone.now()
        self.online_user1 = OnlineUserActivity.objects.create(user=self.user, last_activity=self.time)
        self.assertEqual(OnlineUserActivity.objects.all().count(), 1)


    def test_signup(self):
        response = self.client.get('/signup/', {}, follow=True)
        self.assertTemplateUsed(response, 'signup.html')
        self.failUnless(isinstance(response.context['form'], SignupForm))

    def test_signup_email_confirmation(self):
        response = self.client.post('/signup/', data={'email': 'test1@gmail.com',
                                                      'name': 'test1',
                                                      'gender': True,
                                                      'password1': 'test1',
                                                      'password2': 'test1'}, follow=True)
        self.assertEqual(len(mail.outbox), 1)

        for i in mail.outbox:
            token = i.body.split(' ')[-1]
        token = token[38:-1]
        user = User.objects.get(email='test1@gmail.com')
        user_id = urlsafe_base64_encode(force_bytes(user.pk))

        activation_url = reverse('activate', kwargs={'user_id': user_id, 'token': token})
        activation_url = 'http://testserver' + activation_url
        self.client.get(activation_url, follow=True)

        user.refresh_from_db()

        self.assertTrue(user.is_active)
        self.assertRedirects(response, '/login/')

    def test_signup_email_confirmation_fail(self):
        response = self.client.post('/signup/', data={'email': 'test1@gmail.com',
                                                      'name': 'test1',
                                                      'gender': True,
                                                      'password1': 'test1',
                                                      'password2': 'test1'}, follow=True)
        self.assertEqual(len(mail.outbox), 1)

        user = User.objects.get(email='test1@gmail.com')
        user_id = urlsafe_base64_encode(force_bytes(user.pk))

        activation_url = reverse('activate', kwargs={'user_id': user_id, 'token': 'invalidtoken'})
        activation_url = 'http://testserver' + activation_url
        self.client.get(activation_url, follow=True)

        user.refresh_from_db()

        self.assertFalse(user.is_active)
        self.assertRedirects(response, '/login/')

    def test_login_fail(self):
        user = User.objects.create_user(email='test1@gmail.com', password='test1')
        self.client.post(reverse('login'), {'email': user.email, 'password': 'invalidpassword'})
        self.assertTemplateUsed('login.html')

    def test_login(self):
        self.client.post(reverse('login'), data={'email': 'test@gmail.com', 'password': 'test'})
        self.assertTemplateUsed('profile.html')



class AuthenticationFormTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_auth_form_valid(self):
        data = {'email': 'test1@gmail.com',
                'password1': 'test1',
                'password2': 'test1',
                'name': 'test1',
                'gender': True}
        form = SignupForm(data=data)
        self.assertTrue(form.is_valid())

    def test_auth_form_email_invalid(self):
        data = {'email': 'test1gmailcom',
                'password1': 'test1',
                'password2': 'test1',
                'name': 'test1',
                'gender': True}
        form = SignupForm(data=data)
        self.assertFalse(form.is_valid())

    def test_auth_form_passwords_invalid(self):
        data = {'email': 'test1@gmail.com',
                'password1': 'test1',
                'password2': 'test2',
                'name': 'test1',
                'gender': True}
        form = SignupForm(data=data)
        self.assertFalse(form.is_valid())


    def test_equal_passwords(self):
        response = self.client.post('/signup/', data={'email': 'test2@gmail.com',
                                                      'name': 'test2',
                                                      'gender': True,
                                                      'password1': 'test1',
                                                      'password2': 'test2'}, follow=True)
        self.failIf(response.context['form'].is_valid())
        self.assertEqual(len(mail.outbox), 0)

    def test_email_valid(self):
        response = self.client.post('/signup/', data={'email': 'test3com',
                                                      'name': 'test3',
                                                      'gender': True,
                                                      'password1': 'test3',
                                                      'password2': 'test3'}, follow=True)
        self.failIf(response.context['form'].is_valid())
        self.assertEqual(len(mail.outbox), 0)

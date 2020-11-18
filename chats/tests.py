from django.test import TestCase, Client
from django.utils.encoding import force_bytes
from django.urls import reverse

from user_profile.models import User

from .models import Chat, Message
from .forms import NewChatForm, NewMessageForm, AddUsersToChatForm

from django.test import tag


class ChatsModelTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@gmail.com', password='test', name='test')
        self.chat = Chat.objects.create(title='test_chat', owner=self.user)

        self.user1 = User.objects.create_user(email='test1@gmail.com', password='test1', name='test1')
        self.user2 = User.objects.create_user(email='test2@gmail.com', password='test2', name='test2')

    def test_chat_creation(self):
        chat = Chat.objects.create(title='test_chat1', owner=self.user)
        self.assertTrue(isinstance(chat, Chat))

    def test_chat_deletion(self):
        self.chat.delete()
        self.assertEqual(len(Chat.objects.filter(title='test_chat')), 0)

    def test_message_creation(self):
        message = Message.objects.create(from_user=self.user, chat=self.chat, body='test')
        self.assertTrue(isinstance(message, Message))

    def test_message_deletion(self):
        message = Message.objects.create(from_user=self.user, chat=self.chat, body='test')
        message.delete()
        self.assertEqual(len(Message.objects.filter(from_user=self.user, chat=self.chat, body='test')), 0)


class ChatsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@gmail.com', password='test', name='test')
        self.client.force_login(self.user)

        self.chat = Chat.objects.create(title='test_chat', owner=self.user)
        self.chat.users.add(self.user)

        self.user1 = User.objects.create_user(email='test1@gmail.com', password='test1', name='test1')
        self.user2 = User.objects.create_user(email='test2@gmail.com', password='test2', name='test2')


    def test_messages_view(self):
        response = self.client.get(reverse('messages'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('messages.html')
        self.assertIn(force_bytes(self.chat.title), response.content)

    def test_messages_chat_creation(self):
        response = self.client.post(reverse('messages'), data={'title': 'test_chat1'}, follow=True)
        chat = Chat.objects.get(title='test_chat1')
        self.assertTrue(isinstance(chat, Chat))
        self.assertEqual(response.status_code, 200)
        self.assertIn(force_bytes(chat.title), response.content)

    def test_delete_message(self):
        message = Message.objects.create(from_user=self.user, chat=self.chat, body='test')
        message.refresh_from_db()
        self.client.get(reverse('delete_message', kwargs={'pk': message.pk}))
        self.assertTrue(message.DoesNotExist())

    def test_delete_message_fail(self):
        response = self.client.get(reverse('delete_message', kwargs={'pk': '10'}))
        self.assertRedirects(response, '/messages/')

    def test_chat_view(self):
        response = self.client.get(reverse('chat', kwargs={'pk': self.chat.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('chat.html')
        self.assertIn(force_bytes(self.chat.title), response.content)

    def test_chat_new_message(self):
        data = {'from_user': self.user, 'chat': self.chat, 'body': 'test'}
        response = self.client.post(reverse('chat', kwargs={'pk': self.chat.pk}), data=data)
        message = Message.objects.filter(from_user=self.user, chat=self.chat, body='test').first()
        self.assertTrue(isinstance(message, Message))
        self.assertIn(force_bytes(message.body), response.content)

    def test_edit_chat(self):
        data = {'title': 'test_edit_chat'}
        self.client.post(reverse('edit_chat', kwargs={'pk': self.chat.pk}), data=data, follow=True)
        self.chat.refresh_from_db()
        self.assertEqual(self.chat.title, 'test_edit_chat')
        self.assertTemplateUsed('edit_chat.html')

    def test_edit_chat_fail_not_owner(self):
        data = {'title': 'test_edit_chat'}
        chat = Chat.objects.create(owner=self.user1, title='test_chat1')
        response = self.client.post(reverse('edit_chat', kwargs={'pk': chat.pk}), data=data, follow=True)
        self.chat.refresh_from_db()
        self.assertNotEqual(self.chat.title, 'test_edit_chat')
        self.assertIn(force_bytes('You must be the owner of the chat to edit it.'), response.content)

    def test_delete_chat(self):
        response = self.client.get(reverse('delete_chat', kwargs={'pk': self.chat.pk}), follow=True)
        self.assertRedirects(response, '/messages/')
        self.assertEqual(len(Chat.objects.filter(title='test_chat')), 0)

    def test_delete_chat_not_owner(self):
        chat = Chat.objects.create(owner=self.user1, title='test_chat1')
        response = self.client.get(reverse('delete_chat', kwargs={'pk': chat.pk}), follow=True)
        self.assertEqual(len(Chat.objects.filter(title='test_chat1')), 1)
        self.assertIn(force_bytes('You can only delete your own chats'), response.content)

    def test_delete_chat_doesnt_exist(self):
        response = self.client.get(reverse('delete_chat', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('You can not delete a chat that does not exist'), response.content)

    def test_add_users_to_chat_view(self):
        response = self.client.get(reverse('add_users_to_chat', kwargs={'pk': self.chat.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('add_users_to_chat.html')

    def test_add_users_to_chat_add_users(self):
        response = self.client.post(reverse('add_users_to_chat', kwargs={'pk': self.chat.pk}), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_add_users_to_chat_non_existing_chat(self):
        response = self.client.post(reverse('add_users_to_chat', kwargs={'pk': '10'}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/messages/')

    def test_add_users_to_chat_not_chat_owner(self):
        chat = Chat.objects.create(owner=self.user1, title='test_chat1')
        response = self.client.post(reverse('add_users_to_chat', kwargs={'pk': chat.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(force_bytes('You can only edit your own chats'), response.content)

    def test_chat_users_view(self):
        response = self.client.get(reverse('chat_users', kwargs={'pk': self.chat.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat_users.html')

    def test_chat_users_view_user_not_in_chat(self):
        chat = Chat.objects.create(owner=self.user1, title='test_chat1')
        response = self.client.get(reverse('chat_users', kwargs={'pk': chat.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(force_bytes('You can only view users from your own chats'), response.content)

    def test_remove_user_from_chat(self):
        self.chat.users.add(self.user1)
        response = self.client.get(reverse('remove_user_from_chat',
                                           kwargs={'pk': self.chat.pk,
                                                   'user_pk': self.user1.pk}), follow=True)
        self.assertEqual(len(self.chat.users.all()), 1)
        self.assertEqual(response.status_code, 200)

    def test_remove_user_from_chat_user_not_in_chat(self):
        response = self.client.get(reverse('remove_user_from_chat',
                                           kwargs={'pk': self.chat.pk,
                                                   'user_pk': self.user2.pk}), follow=True)
        self.assertIn(force_bytes('Action not allowed'), response.content)

    def test_remove_user_from_chat_user_does_not_exist(self):
        response = self.client.get(reverse('remove_user_from_chat',
                                           kwargs={'pk': self.chat.pk,
                                                   'user_pk': '10'}), follow=True)
        self.assertIn(force_bytes('User or chat does not exist'), response.content)

    def test_remove_user_from_chat_not_chat_owner(self):
        chat = Chat.objects.create(owner=self.user1, title='test_chat1')
        chat.users.add(self.user1)
        chat.users.add(self.user2)
        response = self.client.get(reverse('remove_user_from_chat',
                                           kwargs={'pk': chat.pk,
                                                   'user_pk': self.user2.pk}), follow=True)
        self.assertEqual(len(chat.users.all()), 2)
        self.assertIn(force_bytes('Action not allowed'), response.content)

    def test_remove_user_from_chat_chat_does_not_exist(self):
        response = self.client.get(reverse('remove_user_from_chat',
                                           kwargs={'pk': '10',
                                                   'user_pk': self.user.pk}), follow=True)
        self.assertIn(force_bytes('User or chat does not exist'), response.content)

    def test_leave_chat(self):
        self.chat.users.add(self.user1)
        self.client.get(reverse('leave_chat', kwargs={'pk': self.chat.pk}), follow=True)
        self.assertEqual(len(self.chat.users.all()), 1)

    def test_leave_chat_chat_does_not_exist(self):
        response = self.client.get(reverse('leave_chat', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('This chat does not exist yet or have been deleted'), response.content)

    def test_leave_chat_last_user_leaving_deletes_chat(self):
        self.client.get(reverse('leave_chat', kwargs={'pk': self.chat.pk}), follow=True)
        chat = Chat.objects.filter(pk=self.chat.pk).first()
        self.assertTrue(chat.DoesNotExist())

class ChatFormTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@gmail.com', password='test', name='test')
        self.user1 = User.objects.create_user(email='test1@gmail.com', password='test1', name='test1')
        self.user2 = User.objects.create_user(email='test2@gmail.com', password='test2', name='test2')
        self.user3 = User.objects.create_user(email='test3@gmail.com', password='test3', name='test3')

        self.user.friends.add(self.user1)
        self.user.friends.add(self.user2)

        self.chat = Chat.objects.create(title='test', owner=self.user)
        self.chat.users.add(self.user1)

        self.client.force_login(self.user)

    def test_new_chat_form_valid(self):
        data = {'title': 'test_chat1'}
        form = NewChatForm(data=data)
        self.assertTrue(form.is_valid())

    def test_new_chat_form_invalid(self):
        data = {'title': ''}
        form = NewChatForm(data=data)
        self.assertFalse(form.is_valid())

    def test_new_message_form_valid(self):
        data = {'from_user': self.user,
                'chat': self.chat,
                'body': 'test'}
        form = NewMessageForm(data=data)
        self.assertTrue(form.is_valid())

    def test_new_message_form_invalid(self):
        data = {'from_user': self.user,
                'chat': self.chat,
                'body': ''}
        form = NewMessageForm(data=data)
        self.assertFalse(form.is_valid())

    def test_add_users_to_chat_form_valid(self):
        friends = self.user.friends.all()
        chat_users = self.chat.users.all()
        queryset = friends.exclude(id__in=chat_users)
        data = {'users': queryset}
        form = AddUsersToChatForm(data=data, queryset=queryset)
        self.assertTrue(form.is_valid())

    def test_add_users_to_chat_form_invalid(self):
        friends = self.user.friends.all()
        chat_users = self.chat.users.all()
        queryset = friends.exclude(id__in=chat_users)
        data = {'users': ''}
        form = AddUsersToChatForm(data=data, queryset=queryset)
        self.assertFalse(form.is_valid())

    def test_add_users_to_chat_form_invalid_adding_not_friends(self):
        friends = self.user.friends.all()
        chat_users = self.chat.users.all()
        queryset = friends.exclude(id__in=chat_users)
        not_friends = User.objects.filter(name='test3')
        data = {'users': not_friends}
        form = AddUsersToChatForm(data=data, queryset=queryset)
        self.assertFalse(form.is_valid())

    def test_add_users_to_chat_form_invalid_adding_already_in_chat(self):
        friends = self.user.friends.all()
        chat_users = self.chat.users.all()
        queryset = friends.exclude(id__in=chat_users)
        already_in = User.objects.filter(name='test1')
        data = {'users': already_in}
        form = AddUsersToChatForm(data=data, queryset=queryset)
        self.assertFalse(form.is_valid())
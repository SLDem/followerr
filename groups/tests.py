from django.test import TestCase, Client, tag
from django.utils.encoding import force_bytes
from django.urls import reverse

from django.core.management import call_command

from .models import Group, GroupJoinRequest, Discussion
from .forms import NewDiscussionForm, NewGroupForm

from user_profile.models import User
from posts.models import Post
from chats.models import Message

from chats.forms import NewMessageForm


class GroupsModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@gmail.com', name='test', password='test')
        self.user1 = User.objects.create_user(email='test1@gmail.com', name='test1', password='test1')

        self.group = Group.objects.create(title='test_group', admin=self.user)
        self.group1 = Group.objects.create(title='test_group1', admin=self.user1)

        self.discussion = Discussion.objects.create(title='test_discussion', author=self.user, group=self.group)

        self.group_join_request = GroupJoinRequest.objects.create(from_user=self.user, to_group=self.group1)

    def test_group_creation(self):
        group = Group.objects.create(title='test_group2', admin=self.user)
        self.assertTrue(isinstance(group, Group))

    def test_group_deletion(self):
        self.group.delete()
        self.assertEqual(len(Group.objects.filter(title='test_group', admin=self.user)), 0)

    def test_discussion_creation(self):
        discussion = Discussion.objects.create(title='test_discussion1', author=self.user, group=self.group)
        self.assertTrue(isinstance(discussion, Discussion))

    def test_discussion_deletion(self):
        self.discussion.delete()
        self.assertEqual(len(Discussion.objects.filter(title='test_discussion', author=self.user, group=self.group)), 0)

    def test_group_join_request_creation(self):
        group_join_request = GroupJoinRequest.objects.create(from_user=self.user1, to_group=self.group)
        self.assertTrue(isinstance(group_join_request, GroupJoinRequest))

    def test_group_join_request_deletion(self):
        self.group_join_request.delete()
        self.assertEqual(len(GroupJoinRequest.objects.filter(from_user=self.user, to_group=self.group1)), 0)


#add search groups tests
class GroupsViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='test@gmail.com', name='test', password='test')
        self.user1 = User.objects.create_user(email='test1@gmail.com', name='test1', password='test1')
        self.user2 = User.objects.create_user(email='test2@gmail.com', name='test2', password='test2')
        self.user3 = User.objects.create_user(email='test3@gmail.com', name='test3', password='test3')
        self.user4 = User.objects.create_user(email='test4@gmail.com', name='test4', password='test4')
        self.client.force_login(self.user)

        self.group = Group.objects.create(title='test_group', admin=self.user)
        self.group.owners.add(self.user)
        self.group.owners.add(self.user1)
        self.group.owners.add(self.user3)
        self.group.users.add(self.user)
        self.group.users.add(self.user1)
        self.group.users.add(self.user2)
        self.group.users.add(self.user4)

        self.group1 = Group.objects.create(title='test_group1', admin=self.user1)

        self.group2 = Group.objects.create(title='test_group2', admin=self.user1)
        self.group2.owners.add(self.user1)
        self.group2.users.add(self.user1)
        self.group2.users.add(self.user)

        self.group3 = Group.objects.create(title='test_group2', admin=self.user1, is_private=True)
        self.group3.users.add(self.user1)
        self.group3.owners.add(self.user1)

        self.discussion = Discussion.objects.create(title='test_discussion', author=self.user, group=self.group)
        self.discussion1 = Discussion.objects.create(title='test_discussion1', author=self.user1, group=self.group1)

        self.group_join_request = GroupJoinRequest.objects.create(from_user=self.user1, to_group=self.group3)

    def test_groups_view(self):
        response = self.client.get(reverse('groups'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'groups.html')

    def test_groups_new_group_creation(self):
        data = {
            'title': 'test_group3',
            'description': 'test_group_description',
            'admin': self.user
        }
        response = self.client.post(reverse('groups'), data=data, follow=True)
        group = Group.objects.filter(title='test_group3').first()
        self.assertIn(self.user, group.owners.all())
        self.assertIn(self.user, group.users.all())
        self.assertEqual(self.user, group.admin)
        self.assertTrue(isinstance(group, Group))
        self.assertRedirects(response, reverse('group_detail', kwargs={'pk': group.pk}))

    def test_groups_search(self):
        response = self.client.get('/groups/?q=test_group2/', follow=True)
        self.assertIn(force_bytes('test_group2'), response.content)
        self.assertIn(force_bytes('Search results:'), response.content)

    def test_group_detail_view(self):
        response = self.client.get(reverse('group_detail', kwargs={'pk': self.group.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group_detail.html')
        self.assertIn(force_bytes(self.group.title), response.content)

    def test_group_detail_view_doesnt_exist(self):
        response = self.client.get(reverse('group_detail', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('Group does not exist'), response.content)

    def test_group_detail_new_post_creation(self):
        data = {'body': 'test_post_from_group'}
        self.client.post(reverse('group_detail', kwargs={'pk': self.group.pk}), data=data, follow=True)
        post = Post.objects.filter(body='test_post_from_group', group=self.group).first()
        self.assertTrue(isinstance(post, Post))

    def test_group_detail_new_post_not_user_admin_or_owner(self):
        self.client.logout()
        self.client.force_login(self.user4)
        data = {'body': 'test_post_from_group'}
        response = self.client.post(reverse('group_detail', kwargs={'pk': self.group.pk}), data=data, follow=True)
        self.assertIn(force_bytes('Action not allowed'), response.content)

    def test_discussions_list_view(self):
        response = self.client.get(reverse('discussions_list', kwargs={'pk': self.group.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discussions.html')
        self.failUnless(isinstance(response.context['form'], NewDiscussionForm))

    def test_discussions_list_view_group_doesnt_exist(self):
        response = self.client.get(reverse('discussions_list', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('Group does not exist'), response.content)

    def test_discussions_list_new_discussion(self):
        data = {'title': 'test_discussion1', 'description': 'test_description'}
        self.client.post(reverse('discussions_list', kwargs={'pk': self.group.pk}), data=data, follow=True)
        discussion = Discussion.objects.filter(title='test_discussion1', group=self.group).first()
        self.assertTrue(isinstance(discussion, Discussion))

    def test_discussion_list_new_discussion_user_not_in_group(self):
        data = {'title': 'test_discussion1', 'description': 'test_description'}
        response = self.client.post(reverse('discussions_list', kwargs={'pk': self.group1.pk}), data=data, follow=True)
        self.assertIn(force_bytes('You have to be a member of the group to create discussions'), response.content)

    def test_discussion_view(self):
        response = self.client.get(reverse('discussion', kwargs={'pk': self.discussion.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'discussion.html')
        self.failUnless(isinstance(response.context['form'], NewMessageForm))

    def test_discussion_view_doesnt_exist(self):
        response = self.client.get(reverse('discussion', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('Discussion does not exist'), response.content)

    def test_discussion_post_new_message(self):
        data = {'body': 'test_message'}
        self.client.post(reverse('discussion', kwargs={'pk': self.discussion.pk}), data=data, follow=True)
        message = Message.objects.filter(body='test_message').first()
        self.assertTrue(isinstance(message, Message))

    def test_discussion_post_new_message_user_not_in_group(self):
        data = {'body': 'test_message'}
        response = self.client.post(reverse('discussion', kwargs={'pk': self.discussion1.pk}), data=data, follow=True)
        self.assertIn(force_bytes('You must be a member of the group to post messages in this discussion'), response.content)

    def test_remove_discussion(self):
        self.client.get(reverse('remove_discussion', kwargs={'pk': self.discussion.pk}), follow=True)
        self.assertEqual(len(Discussion.objects.filter(title='test_discussion')), 0)

    def test_remove_discussion_not_author_or_group_admin(self):
        response = self.client.get(reverse('remove_discussion', kwargs={'pk': self.discussion1.pk}), follow=True)
        self.assertIn(force_bytes('You can not remove this discussion unless you are its author or group admin.'), response.content)

    def test_remove_discussion_doesnt_exist(self):
        response = self.client.get(reverse('remove_discussion', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('Discussion does not exist'), response.content)

    def test_join_or_leave_group_join(self):
        self.client.get(reverse('join_or_leave_group', kwargs={'pk': self.group1.pk}), follow=True)
        self.assertIn(self.user, self.group1.users.all())

    def test_join_or_leave_group_leave(self):
        self.client.get(reverse('join_or_leave_group', kwargs={'pk': self.group2.pk}), follow=True)
        self.assertNotIn(self.user, self.group2.users.all())

    def test_join_or_leave_group_group_doesnt_exist(self):
        response = self.client.get(reverse('join_or_leave_group', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('Group does not exist'), response.content)

    def test_send_group_join_request(self):
        self.client.get(reverse('send_group_request', kwargs={'pk': self.group3.pk}), follow=True)
        group_join_request = GroupJoinRequest.objects.filter(from_user=self.user, to_group=self.group3).first()
        self.assertTrue(isinstance(group_join_request, GroupJoinRequest))

    def test_send_group_join_request_not_private_group(self):
        response = self.client.get(reverse('send_group_request', kwargs={'pk': self.group1.pk}), follow=True)
        self.assertIn(force_bytes('This group is not private'), response.content)

    def test_send_group_join_request_group_doesnt_exist(self):
        response = self.client.get(reverse('send_group_request', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('Group does not exist'), response.content)

    def test_cancel_group_request(self):
        GroupJoinRequest.objects.create(from_user=self.user, to_group=self.group3)
        self.client.get(reverse('cancel_group_request', kwargs={'pk': self.group3.pk}), follow=True)
        self.assertEqual(len(GroupJoinRequest.objects.filter(from_user=self.user, to_group=self.group3)), 0)

    def test_cancel_group_request_group_doesnt_exist(self):
        response = self.client.get(reverse('cancel_group_request', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('Group does not exist'), response.content)

    def test_cancel_group_request_request_doesnt_exist(self):
        response = self.client.get(reverse('cancel_group_request', kwargs={'pk': self.group3.pk}), follow=True)
        self.assertIn(force_bytes('Group join request does not exist'), response.content)

    def test_cancel_group_request_group_not_private(self):
        response = self.client.get(reverse('cancel_group_request', kwargs={'pk': self.group1.pk}), follow=True)
        self.assertIn(force_bytes('Group is not private'), response.content)

    def test_accept_group_request(self):
        GroupJoinRequest.objects.create(from_user=self.user, to_group=self.group3)
        self.client.logout()
        self.client.force_login(self.user1)
        self.client.get(reverse('accept_group_request', kwargs={'pk': self.group3.pk, 'user_pk': self.user.pk}), follow=True)
        self.assertIn(self.user, self.group3.users.all())

    def test_accept_group_request_no_permission(self):
        response = self.client.get(reverse('accept_group_request', kwargs={'pk': self.group3.pk, 'user_pk': self.user1.pk}), follow=True)
        self.assertIn(force_bytes('Action not allowed'), response.content)

    def test_accept_group_request_group_does_not_exist(self):
        response = self.client.get(reverse('accept_group_request', kwargs={'pk': '10', 'user_pk': self.user1.pk}),
                        follow=True)
        self.assertIn(force_bytes('Group, user or join request does not exist'), response.content)

    def test_accept_group_request_request_does_not_exist(self):
        self.client.logout()
        self.client.force_login(self.user1)
        response = self.client.get(reverse('accept_group_request', kwargs={'pk': self.group3.pk, 'user_pk': self.user2.pk}),
                        follow=True)
        self.assertIn(force_bytes('Group, user or join request does not exist'), response.content)

    def test_accept_group_request_user_does_not_exist(self):
        self.client.logout()
        self.client.force_login(self.user1)
        response = self.client.get(reverse('accept_group_request', kwargs={'pk': self.group3.pk, 'user_pk': '10'}),
                        follow=True)
        self.assertIn(force_bytes('Group, user or join request does not exist'), response.content)

    def test_delete_group_request(self):
        self.client.logout()
        self.client.force_login(self.user1)
        self.client.get(reverse('delete_group_request', kwargs={'pk': self.group3.pk, 'user_pk': self.user1.pk}),
                                   follow=True)
        self.assertEqual(len(GroupJoinRequest.objects.filter(from_user=self.user1, to_group=self.group3)), 0)

    def test_delete_group_request_no_permission(self):
        response = self.client.get(reverse('delete_group_request', kwargs={'pk': self.group3.pk, 'user_pk': self.user1.pk}),
                        follow=True)
        self.assertIn(force_bytes('Action not allowed'), response.content)

    def test_delete_group_request_group_does_not_exist(self):
        self.client.logout()
        self.client.force_login(self.user1)
        response = self.client.get(reverse('delete_group_request', kwargs={'pk': '10', 'user_pk': self.user1.pk}),
                        follow=True)
        self.assertIn(force_bytes('Group, user or join request does not exist'), response.content)

    def test_delete_group_request_request_does_not_exist(self):
        self.client.logout()
        self.client.force_login(self.user1)
        response = self.client.get(reverse('delete_group_request', kwargs={'pk': self.group3.pk, 'user_pk': self.user2.pk}),
                        follow=True)
        self.assertIn(force_bytes('Group, user or join request does not exist'), response.content)

    def test_delete_group_request_user_does_not_exist(self):
        self.client.logout()
        self.client.force_login(self.user1)
        response = self.client.get(reverse('delete_group_request', kwargs={'pk': self.group3.pk, 'user_pk': '10'}),
                        follow=True)
        self.assertIn(force_bytes('Group, user or join request does not exist'), response.content)

    def test_group_management_view(self):
        response = self.client.get(reverse('group_management', kwargs={'pk': self.group.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group_management.html')
        self.failUnless(isinstance(response.context['form'], NewGroupForm))

    def test_group_management_view_fail(self):
        response = self.client.get(reverse('group_management', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('Group does not exist'), response.content)

    def test_group_management_edit_group(self):
        data = {'title': 'test_group_title_edit', 'description': 'test_group_description_edit'}
        self.client.post(reverse('group_management', kwargs={'pk': self.group.pk}), data=data, follow=True)
        group = Group.objects.filter(title='test_group_title_edit', description='test_group_description_edit').first()
        self.assertTrue(isinstance(group, Group))

    def test_group_management_edit_group_not_owner(self):
        data = {'title': 'test_group_title_edit', 'description': 'test_group_description_edit'}
        response = self.client.post(reverse('group_management', kwargs={'pk': self.group3.pk}), data=data, follow=True)
        self.assertIn(force_bytes('You can only manage your own groups'), response.content)

    def test_group_users_view(self):
        response = self.client.get(reverse('group_users', kwargs={'pk': self.group.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group_users.html')

    def test_group_users_view_fail(self):
        response = self.client.get(reverse('group_users', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('Group does not exist'), response.content)

    def test_group_users_private_not_in(self):
        response = self.client.get(reverse('group_users', kwargs={'pk': self.group3.pk}), follow=True)
        self.assertIn(force_bytes('You must be a member of this group to view its participants'), response.content)

    def test_group_users_private_in(self):
        self.group3.users.add(self.user)
        response = self.client.get(reverse('group_users', kwargs={'pk': self.group3.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group_users.html')

    def test_remove_user_from_group(self):
        self.client.post(reverse('remove_user_from_group', kwargs={'pk': self.group.pk, 'user_pk': self.user2.pk}), follow=True)
        self.assertNotIn(self.user2, self.group.users.all())

    def test_remove_user_from_group_group_doesnt_exist(self):
        response = self.client.get(reverse('remove_user_from_group', kwargs={'pk': '10', 'user_pk': self.user4.pk}), follow=True)
        self.assertIn(force_bytes('Group or user does not exist'), response.content)

    def test_remove_user_from_group_user_doesnt_exist(self):
        response = self.client.get(reverse('remove_user_from_group', kwargs={'pk': self.group.pk, 'user_pk': '10'}), follow=True)
        self.assertIn(force_bytes('Group or user does not exist'), response.content)

    def test_remove_user_from_group_remove_user_current_user_is_user(self):
        self.client.logout()
        self.client.force_login(self.user2)
        response = self.client.post(reverse('remove_user_from_group', kwargs={'pk': self.group.pk, 'user_pk': self.user4.pk}), follow=True)
        self.assertIn(force_bytes('You can only remove users from your own groups'), response.content)

    def test_remove_user_from_group_remove_admin_current_user_is_user(self):
        self.client.logout()
        self.client.force_login(self.user2)
        response = self.client.post(reverse('remove_user_from_group', kwargs={'pk': self.group.pk, 'user_pk': self.user.pk}), follow=True)
        self.assertIn(force_bytes('You can only remove users from your own groups'), response.content)

    def test_remove_user_from_group_remove_user_current_user_is_owner(self):
        self.client.logout()
        self.client.force_login(self.user2)
        response = self.client.post(reverse('remove_user_from_group', kwargs={'pk': self.group.pk, 'user_pk': self.user1.pk}), follow=True)
        self.assertIn(force_bytes('You can only remove users from your own groups'), response.content)

    def test_remove_user_from_group_remove_owner_current_user_is_owner(self):
        self.client.logout()
        self.client.force_login(self.user1)
        response = self.client.post(reverse('remove_user_from_group', kwargs={'pk': self.group.pk, 'user_pk': self.user3.pk}), follow=True)
        self.assertIn(force_bytes('You can not remove other owners or admin'), response.content)

    def test_remove_user_from_group_remove_admin_current_user_is_owner(self):
        self.client.logout()
        self.client.force_login(self.user1)
        response = self.client.post(reverse('remove_user_from_group', kwargs={'pk': self.group.pk, 'user_pk': self.user.pk}), follow=True)
        self.assertIn(force_bytes('You can not remove other owners or admin'), response.content)

    def test_remove_user_from_group_remove_owner_current_user_is_admin(self):
        self.client.post(reverse('remove_user_from_group', kwargs={'pk': self.group.pk, 'user_pk': self.user1.pk}), follow=True)
        self.assertNotIn(self.user1, self.group.users.all())

    def test_remove_user_from_group_remove_user_current_user_is_admin(self):
        self.client.post(reverse('remove_user_from_group', kwargs={'pk': self.group.pk, 'user_pk': self.user2.pk}), follow=True)
        self.assertNotIn(self.user2, self.group.users.all())

    def test_delete_group_user_is_admin(self):
        self.client.get(reverse('delete_group', kwargs={'pk': self.group.pk}), follow=True)
        self.assertEqual(len(Group.objects.filter(title='test_group')), 0)

    def test_delete_group_user_is_not_admin(self):
        response = self.client.get(reverse('delete_group', kwargs={'pk': self.group3.pk}), follow=True)
        self.assertIn(force_bytes('You can only delete groups you are admin of'), response.content)

    def test_delete_group_doesnt_exist(self):
        response = self.client.get(reverse('delete_group', kwargs={'pk': '10'}), follow=True)
        self.assertIn(force_bytes('Group does not exist'), response.content)

    def test_make_owner_group_doesnt_exist(self):
        response = self.client.get(reverse('make_owner', kwargs={'pk': '10', 'user_pk': self.user4.pk}), follow=True)
        self.assertIn(force_bytes('User or group does not exist'), response.content)

    def test_make_owner_user_doesnt_exist(self):
        response = self.client.get(reverse('make_owner', kwargs={'pk': self.group.pk, 'user_pk': '10'}), follow=True)
        self.assertIn(force_bytes('User or group does not exist'), response.content)

    def test_make_owner_user_making_user(self):
        self.client.logout()
        self.client.force_login(self.user2)
        response = self.client.get(reverse('make_owner', kwargs={'pk': self.group.pk, 'user_pk': self.user4.pk}), follow=True)
        self.assertIn(force_bytes('Action not allowed'), response.content)

    def test_make_owner_user_making_owner(self):
        self.client.logout()
        self.client.force_login(self.user2)
        response = self.client.get(reverse('make_owner', kwargs={'pk': self.group.pk, 'user_pk': self.user2.pk}), follow=True)
        self.assertIn(force_bytes('Action not allowed'), response.content)

    def test_make_owner_user_making_admin(self):
        self.client.logout()
        self.client.force_login(self.user2)
        response = self.client.get(reverse('make_owner', kwargs={'pk': self.group.pk, 'user_pk': self.user1.pk}), follow=True)
        self.assertIn(force_bytes('Action not allowed'), response.content)

    def test_make_owner_owner_making_user(self):
        self.client.logout()
        self.client.force_login(self.user1)
        self.client.get(reverse('make_owner', kwargs={'pk': self.group.pk, 'user_pk': self.user4.pk}), follow=True)
        self.assertIn(self.user4, self.group.users.all())

    def test_make_owner_owner_making_owner(self):
        self.client.logout()
        self.client.force_login(self.user1)
        response = self.client.get(reverse('make_owner', kwargs={'pk': self.group.pk, 'user_pk': self.user3.pk}), follow=True)
        self.assertIn(force_bytes('User already listed as owner of the group'), response.content)

    def test_make_owner_owner_making_admin(self):
        self.client.logout()
        self.client.force_login(self.user1)
        response = self.client.get(reverse('make_owner', kwargs={'pk': self.group.pk, 'user_pk': self.user.pk}), follow=True)
        self.assertIn(force_bytes('User already listed as owner of the group'), response.content)

    def test_make_owner_admin_making_user(self):
        self.client.get(reverse('make_owner', kwargs={'pk': self.group.pk, 'user_pk': self.user4.pk}), follow=True)
        self.assertIn(self.user4, self.group.users.all())

    def test_make_owner_admin_making_owner(self):
        response = self.client.get(reverse('make_owner', kwargs={'pk': self.group.pk, 'user_pk': self.user1.pk}), follow=True)
        self.assertIn(force_bytes('User already listed as owner of the group'), response.content)

    def test_remove_owner_group_or_user_doesnt_exist(self):
        response = self.client.get(reverse('remove_owner', kwargs={'pk': '10', 'user_pk': self.user1.pk}), follow=True)
        response1 = self.client.get(reverse('remove_owner', kwargs={'pk': self.group.pk, 'user_pk': '10'}), follow=True)
        self.assertIn(force_bytes('User or group does not exist'), response.content)
        self.assertIn(force_bytes('User or group does not exist'), response1.content)

    def test_remove_owner_user_removing(self):
        self.client.logout()
        self.client.force_login(self.user4)
        response = self.client.get(reverse('remove_owner', kwargs={'pk': self.group.pk, 'user_pk': self.user2.pk}), follow=True)
        response1 = self.client.get(reverse('remove_owner', kwargs={'pk': self.group.pk, 'user_pk': self.user1.pk}),follow=True)
        response2 = self.client.get(reverse('remove_owner', kwargs={'pk': self.group.pk, 'user_pk': self.user.pk}),follow=True)
        self.assertIn(force_bytes('You cant perform this action unless you are the admin of this group'), response.content)
        self.assertIn(force_bytes('You cant perform this action unless you are the admin of this group'), response1.content)
        self.assertIn(force_bytes('You cant perform this action unless you are the admin of this group'), response2.content)

    def test_remove_owner_owner_removing(self):
        self.client.logout()
        self.client.force_login(self.user1)
        response = self.client.get(reverse('remove_owner', kwargs={'pk': self.group.pk, 'user_pk': self.user4.pk}), follow=True)
        response1 = self.client.get(reverse('remove_owner', kwargs={'pk': self.group.pk, 'user_pk': self.user3.pk}),follow=True)
        response2 = self.client.get(reverse('remove_owner', kwargs={'pk': self.group.pk, 'user_pk': self.user.pk}),follow=True)
        self.assertIn(force_bytes('You cant perform this action unless you are the admin of this group'), response.content)
        self.assertIn(force_bytes('You cant perform this action unless you are the admin of this group'), response1.content)
        self.assertIn(force_bytes('You cant perform this action unless you are the admin of this group'), response2.content)

    def test_remove_owner_admin_removing_user(self):
        response = self.client.get(reverse('remove_owner', kwargs={'pk': self.group.pk, 'user_pk': self.user4.pk}), follow=True)
        self.assertIn(force_bytes('This user is not the owner of the group'), response.content)

    def test_remove_owner_admin_removing_owner(self):
        self.client.get(reverse('remove_owner', kwargs={'pk': self.group.pk, 'user_pk': self.user1.pk}), follow=True)
        self.assertNotIn(self.user1, self.group.owners.all())

    def test_remove_owner_admin_removing_admin(self):
        response = self.client.get(reverse('remove_owner', kwargs={'pk': self.group.pk, 'user_pk': self.user.pk}), follow=True)
        self.assertIn(force_bytes('You cant remove your own owner rights'), response.content)


class GroupsFormsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='test@gmail.com', name='test', password='test')
        self.client.force_login(self.user)

    def test_new_group_form_valid(self):
        data = {'title': 'test_group1', 'description': 'test_group_description', 'admin': self.user}
        form = NewGroupForm(data=data)
        self.assertTrue(form.is_valid())

    def test_new_group_form_invalid_no_title(self):
        data = {'title': '', 'description': 'test_group_description', 'admin': self.user}
        form = NewGroupForm(data=data)
        self.assertFalse(form.is_valid())

    def test_new_group_form_invalid_no_description(self):
        data = {'title': 'test_group1', 'description': '', 'admin': self.user}
        form = NewGroupForm(data=data)
        self.assertFalse(form.is_valid())

    def test_new_discussion_form_valid(self):
        data = {'title': 'test_discussion', 'description': 'test_description', 'author': self.user}
        form = NewDiscussionForm(data=data)
        self.assertTrue(form.is_valid())

    def test_new_discussion_form_invalid_no_title(self):
        data = {'title': '', 'description': 'test_description', 'author': self.user}
        form = NewDiscussionForm(data=data)
        self.assertFalse(form.is_valid())

    def test_new_discussion_form_invalid_no_description(self):
        data = {'title': 'test_discussion', 'description': '', 'author': self.user}
        form = NewDiscussionForm(data=data)
        self.assertFalse(form.is_valid())


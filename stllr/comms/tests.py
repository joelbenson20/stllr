from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from pages.models import Page, Domain
from forums.models import Post
from stars.models import Star
from users.models import ContactRelation
from comms.models import Notification

User = get_user_model()


class CommsTestBase(TestCase):
    def setUp(self):
        self.stella = User.objects.create_user(username='stella')
        self.stella.set_password('pass')
        self.stella.save()
        self.stranger = User.objects.create_user(username='stranger')
        self.stranger.set_password('pass')
        self.stranger.save()
        self.domain = Domain.objects.create(name='example.com')
        self.page = Page.objects.create(
            canonical='example.com/page',
            title='Example Page',
            domain=self.domain,
        )
        self.post = Post.objects.create(
            author=self.stella,
            page=self.page,
            content='Hello world',
        )
        self.page_ct = ContentType.objects.get_for_model(Page)
        self.post_ct = ContentType.objects.get_for_model(Post)


class ShareObjectTests(CommsTestBase):

    def setUp(self):
        super().setUp()
        ContactRelation.objects.create(
            from_user=self.stella,
            to_user=self.stranger,
            status=ContactRelation.Status.ACCEPTED,
        )

    def test_unauthenticated_user_is_redirected(self):
        response = self.client.post(reverse('comms:share_object'))
        self.assertEqual(response.status_code, 302)

    def test_missing_parameters_returns_404(self):
        self.client.login(username='stella', password='pass')
        response = self.client.post(reverse('comms:share_object'), {})
        self.assertEqual(response.status_code, 404)

    def test_non_contact_recipient_returns_403(self):
        outsider = User.objects.create_user(username='outsider')
        outsider.set_password('pass')
        outsider.save()
        self.client.login(username='stella', password='pass')
        response = self.client.post(reverse('comms:share_object'), {
            'object_type': 'page',
            'object_id': self.page.id,
            'contact_id': outsider.id,
        })
        self.assertEqual(response.status_code, 403)

    def test_sharing_page_creates_unread_notification(self):
        self.client.login(username='stella', password='pass')
        self.client.post(reverse('comms:share_object'), {
            'object_type': 'page',
            'object_id': self.page.id,
            'contact_id': self.stranger.id,
        })
        self.assertTrue(Notification.objects.filter(
            recipient=self.stranger,
            event=Notification.Event.PAGE_SHARED,
            read=False,
        ).exists())

    def test_sharing_post_creates_unread_notification(self):
        self.client.login(username='stella', password='pass')
        self.client.post(reverse('comms:share_object'), {
            'object_type': 'post',
            'object_id': self.post.id,
            'contact_id': self.stranger.id,
        })
        self.assertTrue(Notification.objects.filter(
            recipient=self.stranger,
            event=Notification.Event.POST_SHARED,
            read=False,
        ).exists())

    def test_invalid_object_type_returns_400(self):
        self.client.login(username='stella', password='pass')
        response = self.client.post(reverse('comms:share_object'), {
            'object_type': 'invalid',
            'object_id': self.page.id,
            'contact_id': self.stranger.id,
        })
        self.assertEqual(response.status_code, 400)


class NotificatoinSignalTests(CommsTestBase):

    def test_post_starred_notifies_author(self):
        Star.objects.create(user=self.stranger, object_ct=self.post_ct, object_id=self.post.id)
        self.assertTrue(Notification.objects.filter(
            recipient=self.stella,
            event=Notification.Event.POST_STARRED,
        ).exists())

    def test_post_replied_notifies_parent_author(self):
        Post.objects.create(
            author=self.stranger,
            page=self.page,
            content='A reply',
            parent=self.post,
        )
        self.assertTrue(Notification.objects.filter(
            recipient=self.stella,
            event=Notification.Event.POST_REPLIED,
        ).exists())

    def test_self_reply_does_not_notify(self):
        Post.objects.create(
            author=self.stella,
            page=self.page,
            content='A self-reply',
            parent=self.post,
        )
        self.assertFalse(Notification.objects.filter(
            recipient=self.stella,
            event=Notification.Event.POST_REPLIED,
        ).exists())

    def test_contact_request_notifies_recipient(self):
        ContactRelation.objects.create(
            from_user=self.stranger,
            to_user=self.stella,
            status=ContactRelation.Status.PENDING,
        )
        self.assertTrue(Notification.objects.filter(
            recipient=self.stella,
            event=Notification.Event.CONTACT_REQUEST,
        ).exists())

    def test_contact_accepted_notifies_sender(self):
        relation = ContactRelation.objects.create(
            from_user=self.stranger,
            to_user=self.stella,
            status=ContactRelation.Status.PENDING,
        )
        relation.status = ContactRelation.Status.ACCEPTED
        relation.save()
        self.assertTrue(Notification.objects.filter(
            recipient=self.stranger,
            event=Notification.Event.CONTACT_ACCEPTED,
        ).exists())

    def test_page_also_starred_notifies_contact(self):
        ContactRelation.objects.create(
            from_user=self.stella,
            to_user=self.stranger,
            status=ContactRelation.Status.ACCEPTED,
        )
        Star.objects.create(user=self.stella, object_ct=self.page_ct, object_id=self.page.id)
        Star.objects.create(user=self.stranger, object_ct=self.page_ct, object_id=self.page.id)
        self.assertTrue(Notification.objects.filter(
            recipient=self.stella,
            event=Notification.Event.PAGE_ALSO_STARRED,
        ).exists())

    def test_post_also_starred_notifies_contact(self):
        ContactRelation.objects.create(
            from_user=self.stella,
            to_user=self.stranger,
            status=ContactRelation.Status.ACCEPTED,
        )
        Star.objects.create(user=self.stella, object_ct=self.post_ct, object_id=self.post.id)
        Star.objects.create(user=self.stranger, object_ct=self.post_ct, object_id=self.post.id)
        self.assertTrue(Notification.objects.filter(
            recipient=self.stella,
            event=Notification.Event.POST_ALSO_STARRED,
        ).exists())

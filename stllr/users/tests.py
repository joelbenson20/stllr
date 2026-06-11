from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import ContactRelation

User = get_user_model()

class ProfileTests(TestCase):

    def setUp(self):
        self.stella = User.objects.create_user(username='stella')
        self.stella.set_password('pass')
        self.stella.save()

    def test_profile_is_publicly_accessible(self):
        response = self.client.get(reverse('users:profile', args=['stella']))
        self.assertEqual(response.status_code, 200)

    def test_nonexistent_profile_returns_404(self):
        response = self.client.get(reverse('users:profile', args=['nobody']))
        self.assertEqual(response.status_code, 404)

class ContactTests(TestCase):

    def setUp(self):
        self.stella = User.objects.create_user(username='stella')
        self.stella.set_password('pass')
        self.stella.save()
        self.stranger = User.objects.create_user(username='stranger')
        self.stranger.set_password('pass')
        self.stranger.save()

    def test_send_request_creates_pending_contact_relation(self):
        self.client.login(username='stella', password='pass')
        self.client.get(reverse('users:send_request', args=['stranger']))
        relation = ContactRelation.objects.filter(from_user=self.stella, to_user=self.stranger).first()
        self.assertIsNotNone(relation)
        self.assertEqual(relation.status, ContactRelation.Status.PENDING)

    def test_accept_request_updates_status_to_accepted(self):
        ContactRelation.objects.create(from_user=self.stranger, to_user=self.stella, status=ContactRelation.Status.PENDING)
        self.client.login(username='stella', password='pass')
        self.client.get(reverse('users:accept_request', args=['stranger']))
        relation = ContactRelation.objects.get(from_user=self.stranger, to_user=self.stella)
        self.assertEqual(relation.status, ContactRelation.Status.ACCEPTED)

    def test_decline_request_removes_relation(self):
        ContactRelation.objects.create(from_user=self.stranger, to_user=self.stella, status=ContactRelation.Status.PENDING)
        self.client.login(username='stella', password='pass')
        self.client.get(reverse('users:decline_request', args=['stranger']))
        self.assertFalse(ContactRelation.objects.filter(from_user=self.stranger, to_user=self.stella).exists())

    def test_remove_contact_removes_relation_initiated_by_self(self):
        ContactRelation.objects.create(from_user=self.stella, to_user=self.stranger, status=ContactRelation.Status.ACCEPTED)
        self.client.login(username='stella', password='pass')
        self.client.get(reverse('users:remove_contact', args=['stranger']))
        self.assertFalse(ContactRelation.objects.filter(from_user=self.stella, to_user=self.stranger).exists())

    def test_remove_contact_removes_relation_initiated_by_other(self):
        ContactRelation.objects.create(from_user=self.stranger, to_user=self.stella, status=ContactRelation.Status.ACCEPTED)
        self.client.login(username='stella', password='pass')
        self.client.get(reverse('users:remove_contact', args=['stranger']))
        self.assertFalse(ContactRelation.objects.filter(from_user=self.stranger, to_user=self.stella).exists())

    
#TODO: Consider whether to keep user muting functionality in forums

#TODO: Decide whether to keep the 'action' model.
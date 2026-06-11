from django.test import TestCase
from django.urls import reverse
from pages.models import Page, Domain

class RoomViewTests(TestCase):

    def setUp(self):
        self.domain = Domain.objects.create(name='example.com')
        self.page = Page.objects.create(
            canonical='example.com/page',
            title='Example Page',
            domain=self.domain,
        )

    def test_room_is_publicly_accessible(self):
        response = self.client.get(reverse('rooms:room', args=[self.page.id]))
        self.assertEqual(response.status_code, 200)

    def test_nonexistent_room_returns_404(self):
        response = self.client.get(reverse('rooms:room', args=[99999]))
        self.assertEqual(response.status_code, 404)

    #TODO: Test the WebSocket consumer with Django Channels's test tooling
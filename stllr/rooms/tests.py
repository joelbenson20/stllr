import asyncio
from datetime import timedelta
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache
from channels.testing import WebsocketCommunicator
from asgiref.sync import sync_to_async
from stllr.asgi import application
from pages.models import Page, Domain
from rooms.models import Broadcast
from rooms.consumers import _get_users, _presence_key
from rooms.tasks import delete_old_broadcasts

User = get_user_model()

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

class RoomConsumerTests(TransactionTestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='stella')
        self.user.set_password('pass')
        self.user.save()
        self.domain = Domain.objects.create(name='example.com')
        self.page = Page.objects.create(
            canonical='example.com/page',
            title='Example Page',
            domain=self.domain
        )

    async def test_unauthenticated_user_cannot_connect(self):
        communicator = WebsocketCommunicator(
            application,
            f'/ws/room/{self.page.id}/',
            headers=[(b'origin', b'http://localhost')]
        )
        connected, _ = await communicator.connect()
        self.assertFalse(connected)
        await communicator.disconnect()

    async def test_authenticated_user_can_connect(self):
        communicator = WebsocketCommunicator(
            application,
            f'/ws/room/{self.page.id}/',
            headers=[(b'origin', b'http://localhost')]
        )
        communicator.scope['user'] = self.user
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_user_added_to_presence_on_connect(self):
        communicator = WebsocketCommunicator(
            application,
            f'/ws/room/{self.page.id}/',
            headers=[(b'origin', b'http://localhost')]
        )
        communicator.scope['user'] = self.user
        await communicator.connect()
        await communicator.receive_json_from()
        await communicator.receive_json_from()

        users = await sync_to_async(_get_users)(f'room_{self.page.id}')
        self.assertIn('stella', users.values())

    async def test_user_removed_from_presence_on_disconnect(self):
        communicator = WebsocketCommunicator(
            application,
            f'/ws/room/{self.page.id}/',
            headers=[(b'origin', b'http://localhost')]
        )
        communicator.scope['user'] = self.user
        await communicator.connect()
        await communicator.receive_json_from()
        await communicator.receive_json_from()

        await communicator.disconnect()
        await asyncio.sleep(0.1)

        users = await sync_to_async(_get_users)(f'room_{self.page.id}')
        self.assertNotIn('stella', users.values())

    async def test_disconnect_broadcasts_left_message(self):
        # Connect first client
        communicator1 = WebsocketCommunicator(
            application,
            f'ws/room/{self.page.id}/',
            headers=[(b'origin', b'http://localhost')]
        )
        communicator1.scope['user'] = self.user
        await communicator1.connect()
        await communicator1.receive_json_from()  # consume "entered" message
        await communicator1.receive_json_from()  # consume presence update

        # Connect second client
        stranger = await User.objects.acreate(username='stranger')
        await sync_to_async(stranger.set_password)('pass')
        await stranger.asave()

        communicator2 = WebsocketCommunicator(
            application,
            f'ws/room/{self.page.id}/',
            headers=[(b'origin', b'http://localhost')]
        )
        communicator2.scope['user'] = stranger
        await communicator2.connect()

        # Consume messages that communicator1 receives when stranger joins
        await communicator1.receive_json_from()  # stranger entered message
        await communicator1.receive_json_from()  # presence update
        # Consume communicator2's own join messages
        await communicator2.receive_json_from()  # entered message
        await communicator2.receive_json_from()  # presence update

        # Disconnect stranger
        await communicator2.disconnect()
        await asyncio.sleep(0.1)

        # communicator1 should receive the "left" message and presence update
        left_msg = await communicator1.receive_json_from()
        presence_msg = await communicator1.receive_json_from()

        self.assertIn('left the room', left_msg['html'])
        self.assertNotIn('stranger', presence_msg['users'])

        await communicator1.disconnect()

    # TODO: Redesign presence cache to be per-user (separate Redis key per user per room)
    # so that individual users can time out independently rather than the entire room
    # cache sharing one TTL. Write presence TTL test after redesign.

    async def test_message_is_saved_to_database(self):
        communicator = WebsocketCommunicator(
            application,
            f'/ws/room/{self.page.id}/',
            headers=[(b'origin', b'http://localhost')]
        )
        communicator.scope['user'] = self.user
        await communicator.connect()
        await communicator.receive_json_from()  # consume "entered the room" message
        await communicator.receive_json_from()  # consume presence update

        await communicator.send_json_to({'content': 'Hello world'})
        await communicator.receive_json_from()  # consume the broadcast message
        await asyncio.sleep(0.1)

        broadcast_exists = await Broadcast.objects.filter(
            user=self.user,
            page=self.page,
            content='Hello world'
        ).aexists()
        self.assertTrue(broadcast_exists)
        await communicator.disconnect()



class BroadcastRetentionTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='stella')
        self.user.set_password('pass')
        self.user.save()
        self.domain = Domain.objects.create(name='example.com')
        self.page = Page.objects.create(
            canonical='example.com/page',
            title='Example Page',
            domain=self.domain,
        )

    def test_broadcasts_older_than_90_days_are_deleted(self):
        broadcast = Broadcast.objects.create(user=self.user, page=self.page, content='Hello')
        Broadcast.objects.filter(pk=broadcast.pk).update(created=timezone.now() - timedelta(days=91))
        delete_old_broadcasts()
        self.assertFalse(Broadcast.objects.filter(pk=broadcast.pk).exists())

    def test_broadcasts_older_than_90_days_are_kept(self):
        broadcast = Broadcast.objects.create(user=self.user, page=self.page, content='Hello')
        delete_old_broadcasts()
        self.assertTrue(Broadcast.objects.filter(pk=broadcast.pk).exists())
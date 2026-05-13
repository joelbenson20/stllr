import json
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from django.template.loader import render_to_string
from asgiref.sync import sync_to_async
from .models import Message


# Authenticate with WS ticket for browser extension
@database_sync_to_async
def get_user_from_ticket(ticket):
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import AnonymousUser
    from django.core.cache import cache
    user_id = cache.get(f'ws_ticket:{ticket}')
    if not user_id:
        return AnonymousUser()
    cache.delete(f'ws_ticket:{ticket}')
    try:
        return get_user_model().objects.get(pk=user_id)
    except Exception:
        return AnonymousUser()


class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.page_id = self.scope['url_route']['kwargs']['page_id']
        self.room_group_name = f'room_{self.page_id}'
        # Done by Claude, requires review
        if not self.user.is_authenticated:
            params = parse_qs(self.scope.get('query_string', b'').decode())
            ticket = params.get('ticket', [None])[0]
            if ticket:
                self.user = await get_user_from_ticket(ticket)
        if not self.user.is_authenticated:
            await self.close()
            return
        # join room group
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        # accept the connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    # receive messages from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        content = data['content']
        now = timezone.now()

        # persist message
        message = await Message.objects.acreate(
            user=self.user, page_id=self.page_id, content=content
        )

        html = await sync_to_async(render_to_string)(
            'messages/message.html',
            context={'message': message},
        )

        # send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'room_message',
                'html': html,
            }
        )

    # receive message from room group
    async def room_message(self, event):
        # send message to WebSocket
        await self.send(json.dumps(event))
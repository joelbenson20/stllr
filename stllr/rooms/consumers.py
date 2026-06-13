import json
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.template.loader import render_to_string
from django.core.cache import cache
from asgiref.sync import sync_to_async
from .models import Broadcast
from pages.models import Page

PRESENCE_TTL = 20 # expires 2 heartbeats after last activity

def _presence_key(room_name):
    return f'presence:{room_name}'

def _get_users(room_name):
    return cache.get(_presence_key(room_name)) or {}

def _set_users(room_name, users):
    cache.set(_presence_key(room_name), users, PRESENCE_TTL)

# Authenticate users with WS ticket for browser extension
@database_sync_to_async
def get_user_from_ticket(ticket):
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import AnonymousUser #TODO: Confirm expired tickets are actively rejected, not just ignored
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
        self.room_name = f'room_{self.page_id}'

        # Verify page_id is a valid page
        try:
            page = await Page.objects.aget(id=self.page_id)
        except Page.DoesNotExist:
            await self.close()
            return

        # Authenticate browser extension users
        if not self.user.is_authenticated:
            params = parse_qs(self.scope.get('query_string', b'').decode())
            ticket = params.get('ticket', [None])[0]
            if ticket:
                self.user = await get_user_from_ticket(ticket)
        if not self.user.is_authenticated:
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.room_name, self.channel_name
        )

        # Accept connection
        await self.accept()

        # Send "entered the room" message
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'room_message',
                'html': f'<p class="text-secondary mb-3"><i>{self.user.username} entered the room.</i></p>'
            }
        )

        # Update room users cache
        users = await sync_to_async(_get_users)(self.room_name)
        users[self.channel_name] = self.user.username
        await sync_to_async(_set_users)(self.room_name, users)

        # Send presence update to room
        await self.channel_layer.group_send(
            self.room_name,
            {'type': 'presence_update', 'users': list(users.values())}
        )

    async def disconnect(self, close_code):

        # Update room users cache
        users = await sync_to_async(_get_users)(self.room_name)
        users.pop(self.channel_name, None)
        await sync_to_async(_set_users)(self.room_name, users)

        # Leave the room
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

        # Send "left the room" message
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'room_message',
                'html': f'<p class="text-secondary mb-3"><i>{self.user.username} left the room.</i></p>'
            }
        )

        # Send presence update
        await self.channel_layer.group_send(
            self.room_name,
            {'type': 'presence_update', 'users': list(users.values())}
        )


    async def receive(self, text_data):
        data = json.loads(text_data)

        if (data.get('type') == 'ping'):    #TODO: This should refresh TTL on a per-user basis. Needs structural change for user-specific records
            users = await sync_to_async(_get_users)(self.room_name)
            await sync_to_async(_set_users)(self.room_name, users)
            return
        
        content = data['content']   #TODO: Add type to broadcast messages
        broadcast = await Broadcast.objects.acreate(
            user=self.user, page_id=self.page_id, content=content
        )

        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'room_message',
                'html': await sync_to_async(render_to_string)(
                    'broadcast/card.html',
                    context={'broadcast': broadcast}
                ),
            }
        )

    async def room_message(self, event):
        await self.send(json.dumps(event))

    async def presence_update(self, event):
        await self.send(json.dumps({
            'type': 'presence_update',
            'users': event['users'],
            'count': len(event['users']),
        }))
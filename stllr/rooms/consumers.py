import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from .models import Message


class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.id = self.scope['url_route']['kwargs']['page_id']
        self.room_group_name = f'chat_{self.id}'
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

    async def persist_message(self, message):
        await Message.objects.acreate(
            user=self.user, page_id=self.id, content=message
        )

    # receive messages from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        now = timezone.now()
        # send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': self.user.username,
                'datetime': now.isoformat(),
            }
        )
        # persist message
        await self.persist_message(message)

    # receive message from room group
    async def chat_message(self, event):
        # send message to WebSocket
        await self.send(text_data=json.dumps(event))
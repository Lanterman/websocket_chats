import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from main.models import Message


class ChatDetailConsumer(WebsocketConsumer):
    def connect(self):
        self.chat_slug = self.scope['url_route']['kwargs']['chat_slug']
        self.user = self.scope['user']
        self.room_group_name = 'chat_%s' % self.chat_slug
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    def is_read(self):
        messages = Message.objects.filter(chat_id_id=self.chat_slug).exclude(owner_id_id=self.user.id)
        [message.is_read.add(self.user) for message in messages]
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {'type': 'message_read', 'message_info': "connect", "user_id": self.user.id}
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if len(text_data_json) != 0:
            message = text_data_json['message']
            message_obj = Message.objects.create(message=message, chat_id_id=self.chat_slug, owner_id_id=self.user.id)
            message_obj.is_read.add(self.user)

            message_info = {
                "message": message.replace("\n", "<br>"),
                "owner_name": self.user.username if len(self.user.username) < 50 else self.user.username[:48] + "...",
                # "owner_url": self.user.get_absolute_url(),
            }
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {'type': 'chat_message', 'message_info': message_info, "user_id": self.user.id}
            )
        self.is_read()

    def message_read(self, event):
        message_info = event["message_info"]
        user_id = event["user_id"]
        self.send(text_data=json.dumps({"message_info": message_info, "user_id": user_id}))

    def chat_message(self, event):
        message_info = event['message_info']
        user_id = event["user_id"]
        self.send(text_data=json.dumps({'message_info': message_info, "user_id": user_id}))

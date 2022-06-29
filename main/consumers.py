import json
from channels.generic.websocket import WebsocketConsumer
from django.db.models import Q

from main.models import Message, Chat


class ChatDetailConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        json_text_data = json.loads(text_data)
        user_id = json_text_data["user_id"]

        chats = Chat.objects.filter(Q(owner_id=user_id) | Q(users=user_id))
        unread_messages = Message.objects.filter(chat_id__in=chats)

        chats_info = []
        for chat in chats:
            count_messages = unread_messages.filter(chat_id=chat.id).count()
            chats_info += [{
                "name": chat.name,
                # "url": chat.get_absolute_url(),
                "count_messages": f"({count_messages})" if count_messages else '',
            }]

        self.send(text_data=json.dumps({'chats_info': chats_info}))

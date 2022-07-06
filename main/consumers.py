import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from main.models import Message, Chat


class MainPageConsumer(WebsocketConsumer):
    """Consumer for main page"""

    def connect(self):
        self.user = self.scope['user']
        self.accept()

    def disconnect(self, close_code):
        print(f"Error code: {close_code}")

    def search_chats(self, data):
        """Search chats by name"""

        search_value = data["search_value"]
        found_chats = Chat.objects.filter(name__icontains=search_value).select_related("owner_id")
        chat_list = []
        for chat in found_chats:
            user_name = chat.owner_id.username
            info_chat = {
                "chat_url": chat.get_absolute_url(),
                "chat_name": chat.name if len(chat.name) <= 25 else chat.name[:25] + "...",
                "chat_owner_url": f"user/{chat.owner_id.username}/",
                "chat_owner_name": user_name if len(user_name) <= 15 else user_name[:15] + "...",
                "is_password": "Да" if chat.password else "Нет"
            }
            chat_list.append(info_chat)

        self.send(text_data=json.dumps({"chats_info_list": chat_list, "type": data["type"]}))

    def create_chat(self, data):
        """Create chat"""

        chat_title = data["chat_title"]
        chat_password = data["chat_password"]
        new_chat = Chat.objects.create(name=chat_title, password=chat_password, owner_id_id=self.user.id)
        new_chat.users.add(self.user)
        Chat.objects.filter(id=new_chat.id).update(slug=new_chat.id)

        self.send(text_data=json.dumps({"type": "create_chat", "chat_slug": new_chat.id}))

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        action_type = text_data_json["type"]
        if action_type == "search":
            self.search_chats(text_data_json)
        elif action_type == "create_chat":
            self.create_chat(text_data_json)
        else:
            chat_id = text_data_json['chat_id']
            Chat.objects.get(id=chat_id).delete()

            self.send(text_data=json.dumps({"type": action_type, "chat_id": chat_id}))


class ChatDetailConsumer(WebsocketConsumer):
    """Consumer for chat detail"""

    def connect(self):
        self.chat_slug = self.scope['url_route']['kwargs']['chat_slug']
        self.user = self.scope['user']
        self.room_group_name = 'chat_%s' % self.chat_slug
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    def is_read(self):
        messages = Message.objects.filter(chat_id_id=self.chat_slug).exclude(owner_id=self.user).exclude(
            is_read=self.user.id)
        [message.is_read.add(self.user) for message in messages]
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {'type': 'message_read', 'message_info': "connect", "user_id": self.user.id}
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if text_data_json["type"] == "send_message":
            message = text_data_json['message']
            message_obj = Message.objects.create(message=message, chat_id_id=self.chat_slug, owner_id_id=self.user.id)
            message_obj.is_read.add(self.user)

            message_info = {
                "message": message.replace("\n", "<br>"),
                "owner_name": self.user.username if len(self.user.username) < 50 else self.user.username[:48] + "...",
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

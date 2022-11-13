from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import Chat


class MainPageConsumer(AsyncJsonWebsocketConsumer):
    """Consumer for main page"""

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.room_group_name = None

    async def connect(self):
        self.user = self.scope['user']
        self.room_group_name = "main_page"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    @database_sync_to_async
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

        return chat_list

    @database_sync_to_async
    def create_chat(self, data):
        """Create chat"""

        chat_title = data["chat_title"]
        chat_password = data["chat_password"]
        chat_password = chat_password if len(chat_password) <= 100 else chat_password[:101]
        new_chat = Chat.objects.create(name=chat_title, password=chat_password, owner_id_id=self.user.id)
        new_chat.users.add(self.user)
        Chat.objects.filter(id=new_chat.id).update(slug=new_chat.id)
        return new_chat.id

    async def receive_json(self, content, **kwargs):
        action_type = content["type"]

        if action_type == "search":
            chat_list = await self.search_chats(content)
            await self.send_json(content={"chats_info_list": chat_list, "type": action_type})
        elif action_type == "create_chat":
            chat_slug = await self.create_chat(content)
            await self.send_json(content={"type": "create_chat", "chat_slug": chat_slug})
        else:
            chat_id = content['chat_id']
            await self.channel_layer.group_send(self.room_group_name, {'type': 'delete_chat', "chat_id": chat_id})

    async def delete_chat(self, event):
        chat_id = event["chat_id"]
        await self.send_json(content={"type": "delete_chat", "chat_id": chat_id})


class ChatDetailConsumer(AsyncJsonWebsocketConsumer):
    """Consumer for chat detail"""

    def __init__(self):
        super().__init__()
        self.chat_slug = None
        self.user = None
        self.room_group_name = None

    async def connect(self):
        self.chat_slug = self.scope['url_route']['kwargs']['chat_slug']
        self.user = self.scope['user']
        self.room_group_name = 'chat_%s' % self.chat_slug
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.is_read()
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def is_read(self):
        """Read messages"""

        await self.channel_layer.group_send(self.room_group_name, {'type': 'message_read', "user_id": self.user.id})

    async def receive_json(self, content, **kwargs):
        action_type = content["type"]
        if action_type == "send_message":
            message = content['message']
            message_info = {
                "message": message.replace("\n", "<br>"),
                "owner_name": self.user.username if len(self.user.username) < 50 else self.user.username[:48] + "...",
                "owner_url": self.user.username,
            }
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'chat_message', 'message_info': message_info, "user_id": self.user.id}
            )
            await self.is_read()
        elif action_type == "update_chat":
            chat_title = content["chat_title"]
            chat_password = content["chat_password"]
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'update_chat', "chat_name": chat_title, "chat_password": chat_password}
            )
        elif action_type == "connect_to_chat":
            user_info = {
                "owner_name": self.user.username if len(self.user.username) < 50 else self.user.username[:48] + "...",
                "owner_url": self.user.username,
            }
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'connect_to_chat', "user_info": user_info}
            )
        elif action_type == "disconnect_from_chat":
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'disconnect_from_chat', "user_username": self.user.username}
            )

    async def message_read(self, event):
        user_id = event["user_id"]
        await self.send_json(content={"type": "message_read", "message_info": "connect", "user_id": user_id})

    async def chat_message(self, event):
        mes_info = event['message_info']
        user_id = event["user_id"]
        await self.send_json(content={"type": "chat_message", 'message_info': mes_info, "user_id": user_id})

    async def update_chat(self, event):
        chat_title = event["chat_name"]
        chat_password = event["chat_password"]
        await self.send_json(content={"type": "update_chat", "chat_name": chat_title, "chat_password": chat_password})

    async def connect_to_chat(self, event):
        user_info = event["user_info"]
        await self.send_json(content={"type": "connect_to_chat", 'user_info': user_info})

    async def disconnect_from_chat(self, event):
        user_username = event["user_username"]
        await self.send_json(content={"type": "disconnect_from_chat", "user_username": user_username})

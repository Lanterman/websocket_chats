from channels.consumer import AsyncConsumer
from django.test import TestCase
from channels.testing import WebsocketCommunicator
from scr.main.consumers import MainPageConsumer, ChatDetailConsumer
from scr.main.models import User, Chat


class Config(TestCase):
    """Main class"""

    user = None
    user_info = {
        "username": "username",
        "password": "test_password",
        "first_name": "test",
        "last_name": "test",
        "email": "test@example.com"
    }

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(**cls.user_info)
        Chat.objects.create(name="test", slug="1", owner_id=cls.user)

    async def launch_websocket_communicator(
            self, consumer: type[AsyncConsumer] = MainPageConsumer, path: str = "/ws/main/"
    ):
        """Launch websocket communicator"""

        communicator = WebsocketCommunicator(consumer.as_asgi(), path)
        communicator.scope['url_route'] = {"kwargs": {"chat_slug": 1}} if path != "/ws/main/" else {}
        communicator.scope["user"] = self.user
        connected, sub_protocol = await communicator.connect()
        assert connected
        return communicator


class TestMainPageConsumer(Config):
    """Testing MainPageConsumer consumer"""

    async def test_delete_chat(self):
        """Testing create chat"""

        test_data = {"chat_id": 1, "type": "delete_chat"}
        communicator = await self.launch_websocket_communicator()

        await communicator.send_json_to({"chat_id": 1, "type": "delete_chat"})
        response = await communicator.receive_json_from()
        assert response == test_data, response

        await communicator.disconnect()


class TestChatDetailConsumer(Config):
    """Testing ChatDetailConsumer consumer"""

    async def test_connect_to_chat(self):
        """Testing connect to chat"""

        test_data = {
            'type': 'connect_to_chat',
            'user_info': {'owner_name': 'username', 'owner_url': 'username'}
        }
        communicator = await self.launch_websocket_communicator(consumer=ChatDetailConsumer, path="/ws/chat/1/")

        response = await communicator.receive_json_from()
        assert response == {'type': 'message_read', 'message_info': 'connect', 'user_id': self.user.id}, response

        await communicator.send_json_to(data={"type": "connect_to_chat"})
        response = await communicator.receive_json_from()
        assert response == test_data, response

        await communicator.disconnect()

    async def test_send_message(self):
        """Testing send message"""

        test_data = {
            "type": "chat_message",
            "message_info": {"message": "test", "owner_name": "username", "owner_url": "username"},
            "user_id": self.user.id
        }
        communicator = await self.launch_websocket_communicator(consumer=ChatDetailConsumer, path="/ws/chat/1/")

        response = await communicator.receive_json_from()
        assert response == {'type': 'message_read', 'message_info': 'connect', 'user_id': self.user.id}, response

        await communicator.send_json_to(data={"type": "send_message", "message": "test"})
        response = await communicator.receive_json_from()
        assert response == test_data, response

        await communicator.disconnect()

    async def test_update_chat(self):
        """Testing update chat name"""

        test_data = {"type": "update_chat", "chat_name": "update_title", "chat_password": ""}
        communicator = await self.launch_websocket_communicator(consumer=ChatDetailConsumer, path="/ws/chat/1/")

        response = await communicator.receive_json_from()
        assert response == {'type': 'message_read', 'message_info': 'connect', 'user_id': self.user.id}, response

        await communicator.send_json_to(data={"type": "update_chat", "chat_title": "update_title", "chat_password": ""})
        response = await communicator.receive_json_from()
        assert response == test_data, response

        await communicator.disconnect()

    async def test_disconnect_from_chat(self):
        """Testing disconnect from chat"""

        test_data = {"type": "disconnect_from_chat", "user_username": self.user.username}
        communicator = await self.launch_websocket_communicator(consumer=ChatDetailConsumer, path="/ws/chat/1/")

        response = await communicator.receive_json_from()
        assert response == {'type': 'message_read', 'message_info': 'connect', 'user_id': self.user.id}, response

        await communicator.send_json_to(data={"type": "disconnect_from_chat"})
        response = await communicator.receive_json_from()
        assert response == test_data, response

        await communicator.disconnect()

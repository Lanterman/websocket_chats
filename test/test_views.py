from django.test import TestCase

from django.contrib.auth.models import User
from django.urls import reverse

from scr.main.models import Chat, Message

user_list = [
    {
        "username": "username",
        "password": "test_password",
        "first_name": "first_name",
        "last_name": "last_name",
        "email": "email@example.com"
    },
    {
        "username": "test",
        "password": "test_password",
        "first_name": "test",
        "last_name": "test",
        "email": "test@example.com"
    }
]

message = {"message": "test message", "owner_id_id": 1, "chat_id_id": 1}


class TestMainPage(TestCase):
    """Testing main page"""

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(**user_list[0])

    def test_redirect_url(self):
        """Testing redirect url, data and template"""

        response = self.client.get(reverse("main_page"))
        assert response.status_code == 302, response.status_code

        response = self.client.get(reverse("main_page"), follow=True)
        assert response.status_code == 200, response.status_code
        assert response.context_data["title"] == "Авторизация", response.context_data
        assert response.template_name == ["main/user_auth.html"], response.template_name

    def test_url_of_authenticated_user(self):
        """Testing url, data and template of authenticated user"""

        self.client.login(username=user_list[0]["username"], password=user_list[0]["password"])
        response = self.client.get(reverse("main_page"))
        assert response.status_code == 200, response.status_code
        assert response.context_data["type_action"] == "Создать чат", response.context_data
        self.assertTemplateUsed(response, "main/main_page.html", "main/modal_window.html")

        self.client.logout()
        response = self.client.get(reverse("main_page"))
        assert response.status_code == 302, response.status_code


class TestChatDetail(TestCase):
    """Testing chat detail view"""

    chat, user_1 = None, None

    @classmethod
    def setUpTestData(cls):
        cls.user_1 = User.objects.create_user(**user_list[0])
        user_2 = User.objects.create_user(**user_list[1])
        cls.chat = Chat.objects.create(name="chat_name", slug=1, owner_id=user_2)
        cls.chat.users.add(cls.user_1)
        cls.chat.users.add(user_2)
        Message.objects.create(message="test", chat_id_id=cls.chat.id, owner_id_id=cls.user_1.id)
        Message.objects.create(message="test", chat_id_id=cls.chat.id, owner_id_id=user_2.id)

    def test_redirect_url(self):
        """Testing redirect url, data and template"""

        response = self.client.get(reverse("chat_detail", kwargs={"chat_slug": 1}))
        assert response.status_code == 302, response.status_code

        response = self.client.get(reverse("chat_detail", kwargs={"chat_slug": 1}), follow=True)
        assert response.status_code == 200, response.status_code
        assert response.context_data["title"] == "Авторизация", response.context_data
        assert response.template_name == ["main/user_auth.html"], response.template_name

    def test_url_of_authenticated_user(self):
        """Testing url, data and template of authenticated user"""

        self.client.login(username=user_list[0]["username"], password=user_list[0]["password"])
        response = self.client.get(reverse("chat_detail", kwargs={"chat_slug": 1}))
        assert response.status_code == 200, response.status_code
        self.assertTemplateUsed(response, "main/chat_detail.html")

        self.client.logout()
        response = self.client.get(reverse("chat_detail", kwargs={"chat_slug": 1}))
        assert response.status_code == 302, response.status_code

    def test_read_message(self):
        """Testing read message"""

        unread_messages = Message.objects.exclude(is_read=self.user_1.id)
        assert len(unread_messages) == 2, len(unread_messages)

        messages = Message.objects.filter(chat_id_id=self.chat.id).exclude(owner_id_id=self.user_1.id).exclude(
            is_read=self.user_1.id)
        [mes.is_read.add(self.user_1) for mes in messages]

        unread_messages = Message.objects.exclude(is_read=self.user_1.id)
        assert len(unread_messages) == 1, len(unread_messages)

    def test_invalid_delete_chat(self):
        """Testing invalid delete chat"""

        self.client.login(username=user_list[0]["username"], password=user_list[0]["password"])
        response = self.client.get(reverse("delete_chat", kwargs={"chat_slug": 1}))
        assert response.status_code == 403, response.status_code

    def test_valid_delete_chat(self):
        """Testing valid delete chat"""

        self.client.login(username=user_list[1]["username"], password=user_list[1]["password"])
        response = self.client.get(reverse("delete_chat", kwargs={"chat_slug": 1}), follow=True)
        assert response.status_code == 200, response.status_code
        self.assertTemplateUsed(response, "main/main_page.html", "main/modal_window.html")

    def test_leave_chat(self):
        """Testing leave chat"""

        count_users_in_chat = len(self.chat.users.all())
        count_chat_message = len(Message.objects.filter(chat_id_id=self.chat.id))
        self.client.login(username=user_list[0]["username"], password=user_list[0]["password"])
        response = self.client.get(reverse("chat_detail", kwargs={"chat_slug": self.chat.id}))
        assert response.status_code == 200, response.status_code
        assert count_users_in_chat == 2, count_users_in_chat
        assert count_chat_message == 2, count_chat_message

        if self.user_1.id != self.chat.owner_id_id and self.user_1 in self.chat.users.all():
            self.chat.users.remove(self.user_1)
            Message.objects.create(message=f"{self.user_1.username} вышел из чата!", chat_id_id=self.chat.id)

        count_users_in_chat = len(self.chat.users.all())
        count_chat_message = len(Message.objects.filter(chat_id_id=self.chat.id))
        assert count_users_in_chat == 1, count_users_in_chat
        assert count_chat_message == 3, count_chat_message

    def test_user_detail(self):
        """Testing user profile"""

        self.client.login(username=user_list[1]["username"], password=user_list[1]["password"])
        response = self.client.get(reverse("user_detail", kwargs={"username": self.user_1.username}))
        assert response.status_code == 200, response.status_code
        self.assertTemplateUsed(response, "main/user_detail.html")

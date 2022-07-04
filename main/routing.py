from django.urls import re_path, path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<chat_slug>\w+)/', consumers.ChatDetailConsumer.as_asgi()),
    path("ws/main/", consumers.MainPageConsumer.as_asgi()),
]

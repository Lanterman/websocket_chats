from django.db.models import Prefetch
from django.shortcuts import render

from main.models import Chat, Message


def main_page(request):
    """Main page"""

    chats = Chat.objects.filter(users=request.user.id).prefetch_related(Prefetch(
        'chat_messages',
        queryset=Message.objects.exclude(is_read=request.user.id),
        to_attr="set_messages"
    ))
    context = {"chats": chats}
    return render(request, 'main/main_page.html', context)


def chat_detail(request, chat_slug):
    """Chat detail"""

    chat = Chat.objects.get(slug=chat_slug)
    chat_messages = Message.objects.filter(chat_id=chat.id).select_related("owner_id")
    context = {"chat": chat, "chat_messages": chat_messages}
    return render(request, "main/chat_detail.html", context)

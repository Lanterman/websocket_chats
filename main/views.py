from django.db.models import Q
from django.shortcuts import render

from main.models import Chat, Message


def main_page(request):
    """Main page"""

    chats = Chat.objects.filter(Q(owner_id=request.user.id) | Q(users=request.user.id))
    unread_messages = Message.objects.filter(chat_id__in=chats).exclude(is_read=request.user.id)

    count_chats_unread_messages = {chat.id: unread_messages.filter(chat_id=chat.id).count() for chat in chats}
    chat_list = [(chat, count_chats_unread_messages[count_unread_messages]) for chat, count_unread_messages in
                 zip(chats, count_chats_unread_messages)]

    context = {"chat_list": chat_list}
    return render(request, 'main/main_page.html', context)


def chat_detail(request, chat_slug):
    """Chat detail"""

    context = {"chat_slug": chat_slug}
    return render(request, "main/chat_detail.html", context)

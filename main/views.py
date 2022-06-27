from django.db.models import Q, Count
from django.shortcuts import render

from main.models import Chat


def main_page(request):
    # Выводить количество непрочитанных сообщений
    chats = Chat.objects.filter(Q(owner_id=request.user.id) | Q(users=request.user.id)).annotate(new_mes=Count("chat_messages"))
    context = {"chats": chats}
    return render(request, 'main/main_page.html', context)

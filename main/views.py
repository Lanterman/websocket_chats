from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView

from main.models import Chat, Message


# def main_page(request):
#     """Main page"""
#
#     my_chats = Chat.objects.filter(users=request.user.id).prefetch_related(Prefetch(
#         'chat_messages',
#         queryset=Message.objects.exclude(is_read=request.user.id),
#         to_attr="set_messages"
#     ))
#     chats_without_me = Chat.objects.exclude(users=request.user.id)
#     context = {"my_chats": my_chats, "chats_without_me": chats_without_me}
#     return render(request, 'main/main_page.html', context)


# def chat_detail(request, chat_slug):
#     """Chat detail"""
#
#     chat = Chat.objects.get(slug=chat_slug)
#     chat_messages = Message.objects.filter(chat_id=chat.id).select_related("owner_id").prefetch_related("is_read")
#     context = {"chat": chat, "chat_messages": chat_messages}
#     return render(request, "main/chat_detail.html", context)


class ListMainPageView(ListView):
    """Main page"""

    context_object_name = "my_chats"
    template_name = "main/main_page.html"

    def get_queryset(self):
        return Chat.objects.filter(users=self.request.user.id).prefetch_related(Prefetch(
            'chat_messages',
            queryset=Message.objects.exclude(is_read=self.request.user.id),
            to_attr="set_messages"
        ))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chats_without_me'] = Chat.objects.exclude(users=self.request.user.id).select_related("owner_id")[:5]
        context['type_action'] = "Создать чат"
        return context


class ChatDetailView(DetailView):
    """Chat detail"""

    context_object_name = "chat"
    slug_url_kwarg = "chat_slug"
    template_name = "main/chat_detail.html"
    queryset = Chat.objects.all().prefetch_related("users")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chat_messages'] = Message.objects.filter(chat_id=self.object.id).select_related(
            "owner_id").prefetch_related("is_read")
        context["type_action"] = "Редактировать чат"
        return context


def user_detail(request, username):
    return render(request, "main/user_detail.html")


@csrf_exempt
def add_message(request, chat_slug):
    """Add message"""

    message = request.POST.get("message")
    message_obj = Message.objects.create(message=message, chat_id_id=chat_slug, owner_id_id=request.user.id)
    message_obj.is_read.add(request.user)
    return HttpResponse(status=200)


@csrf_exempt
def update_chat(request, chat_slug):
    """Update chat"""

    chat_password = request.POST.get("password")
    chat_title = request.POST.get("title")
    chat_password = chat_password if len(chat_password) <= 100 else chat_password[:101]
    Chat.objects.filter(id=chat_slug).update(name=chat_title, password=chat_password)
    return HttpResponse(status=200)


def is_read(request, chat_slug):
    """Read unread messages"""

    messages = Message.objects.filter(chat_id_id=chat_slug).exclude(owner_id=request.user).exclude(
        is_read=request.user.id)
    [message.is_read.add(request.user) for message in messages]
    return HttpResponse(status=200)


def delete_chat(request, chat_slug):
    """Delete chat if you are owner"""

    chat = Chat.objects.filter(id=chat_slug)
    if request.user.id == chat[0].owner_id_id:
        chat.delete()
        return redirect(reverse('main_page'))
    raise PermissionDenied()


def leave_chat(request, chat_slug):
    """Leave chat if you aren't owner and are member of chat"""

    chat = Chat.objects.filter(id=chat_slug)[0]
    if request.user.id != chat.owner_id_id:
        if request.user in chat.users.all():
            chat.users.remove(request.user)
            return redirect(reverse('main_page'))
    raise PermissionDenied()


def connect_to_chat(request, chat_slug):
    """Connect user to chat"""

    chat = Chat.objects.get(slug=chat_slug)
    chat.users.add(request.user)
    return HttpResponse(status=201)

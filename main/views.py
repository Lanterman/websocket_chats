from django.db.models import Prefetch
from django.shortcuts import render
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
        return context


class ChatDetailView(DetailView):
    """Chat detail"""

    context_object_name = "chat"
    slug_url_kwarg = "chat_slug"
    template_name = "main/chat_detail.html"
    queryset = Chat.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chat_messages'] = Message.objects.filter(chat_id=self.object.id).select_related(
            "owner_id").prefetch_related("is_read")
        return context

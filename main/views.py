from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, CreateView

from main.forms import RegisterUserForm, LoginUserForm
from main.models import Chat, Message


class ListMainPageView(LoginRequiredMixin, ListView):
    """Main page"""

    context_object_name = "my_chats"
    template_name = "main/main_page.html"
    login_url = "/login/"

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


class ChatDetailView(LoginRequiredMixin, DetailView):
    """Chat detail"""

    context_object_name = "chat"
    slug_url_kwarg = "chat_slug"
    template_name = "main/chat_detail.html"
    login_url = "/login/"
    queryset = Chat.objects.all().prefetch_related("users")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chat_messages'] = Message.objects.filter(chat_id=self.object.id).select_related(
            "owner_id").prefetch_related("is_read")
        context["type_action"] = "Редактировать чат"
        return context


@login_required(login_url='/login/')
def user_detail(request, username):
    user = User.objects.get(username=username)
    return render(request, "main/user_detail.html", {"user": user})


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'main/user_auth.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        context["errors"] = "Ошибка регистрации! Попробуйте еще раз."
        context["button"] = "Регистрация"
        context["redirect_name"] = "Уже есть аккаунт?"
        context["redirect"] = "login"
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(reverse('main_page'))


def logout_view(request):
    logout(request)
    return redirect(reverse('main_page'))


class LoginUser(LoginView):
    """User authorization"""

    template_name = 'main/user_auth.html'
    form_class = LoginUserForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Авторизация'
        context["errors"] = "Такого пользователя не существует!"
        context["button"] = "Войти"
        context["redirect_name"] = "Зарегистрироваться"
        context["redirect"] = "register"
        return context


@csrf_exempt
def add_message(request, chat_slug):
    """Add message"""

    message = request.POST.get("message")
    if message is not None:
        message_obj = Message.objects.create(message=message, chat_id_id=chat_slug, owner_id_id=request.user.id)
        message_obj.is_read.add(request.user)
        return HttpResponse(status=200)
    raise PermissionDenied()


@csrf_exempt
def update_chat(request, chat_slug):
    """Update chat"""

    chat_password = request.POST.get("password")
    chat_title = request.POST.get("title")
    if chat_password is not None:
        chat_password = chat_password if len(chat_password) <= 100 else chat_password[:101]
        Chat.objects.filter(id=chat_slug).update(name=chat_title, password=chat_password)
        return HttpResponse(status=200)
    raise PermissionDenied()


@csrf_exempt
def is_read(request, chat_slug):
    """Read unread messages"""

    if request.POST.get("agree"):
        messages = Message.objects.filter(chat_id_id=chat_slug).exclude(owner_id=request.user).exclude(
            is_read=request.user.id)
        [message.is_read.add(request.user) for message in messages]
        return HttpResponse(status=200)
    raise PermissionDenied()


@csrf_exempt
def delete_chat(request, chat_slug):
    """Delete chat if you are owner"""

    chat = Chat.objects.filter(id=chat_slug)
    if request.user.id == chat[0].owner_id_id:
        chat.delete()
        if request.POST.get("type") == "main_page":
            return HttpResponse(status=200)
        return redirect(reverse('main_page'))
    raise PermissionDenied()


def leave_chat(request, chat_slug):
    """Leave chat if you aren't owner and are member of chat"""

    chat = Chat.objects.filter(id=chat_slug)[0]
    if request.user.id != chat.owner_id_id:
        if request.user in chat.users.all():
            chat.users.remove(request.user)
            message_obj = Message.objects.create(message=f"{request.user.username} вышел из чата!", chat_id_id=chat_slug)
            message_obj.is_read.add(request.user)
            return redirect(reverse('main_page'))
    raise PermissionDenied()


@csrf_exempt
def connect_to_chat(request, chat_slug):
    """Connect user to chat"""

    if request.POST.get("agree"):
        chat = Chat.objects.get(slug=chat_slug)
        chat.users.add(request.user)

        message_obj = Message.objects.create(message=f"{request.user.username} присоединился к чату!", chat_id_id=chat_slug)
        message_obj.is_read.add(request.user)
        return HttpResponse(status=201)
    raise PermissionDenied()

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Chat(models.Model):
    """Chat model for conversation among users"""
    name = models.CharField(verbose_name='name', max_length=50)
    slug = models.CharField(verbose_name="URL", max_length=50, unique=True,
                            help_text="Use only prime numbers! Filling with ID")
    is_password = models.BooleanField(default=False, verbose_name="is_password")
    pub_date = models.DateTimeField(verbose_name="set_data", auto_now_add=True)
    owner_id = models.ForeignKey(User, verbose_name="owner", on_delete=models.SET_NULL, related_name="user_chats",
                                 null=True)
    users = models.ManyToManyField(User, verbose_name="users", blank=True)

    class Meta:
        verbose_name = "Chat"
        verbose_name_plural = "Chats"

    def __str__(self):
        return f"{self.id} - owner_id: {self.name}"

    def get_absolute_url(self):
        return reverse('chat', kwargs={'chat_slug': self.slug})


class Message(models.Model):
    """Chat message"""
    message = models.TextField(verbose_name="message", blank=True)
    is_read = models.BooleanField(verbose_name='is_read ', default=False)  # сделать manytomany для user, если нет пользователя в поле, значит не прочитано
    pub_date = models.DateTimeField(verbose_name="set_data", auto_now_add=True)
    owner_id = models.ForeignKey(User, verbose_name="owner", on_delete=models.SET_NULL, related_name="user_messages",
                                 null=True)
    chat_id = models.ForeignKey(Chat, verbose_name="chat_id", on_delete=models.CASCADE, related_name="chat_messages")

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"Chat_id: {self.chat_id} - owner_id: {self.owner_id} - message_id: {self.pk}"

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class Chat(models.Model):
    """Chat model for conversation among users"""
    name = models.CharField(verbose_name='name', max_length=50)
    slug = models.CharField(verbose_name="URL", max_length=50, unique=True,
                            help_text="Use only prime numbers! Filling with ID")
    password = models.CharField(verbose_name="password", blank=True, max_length=100)
    pub_date = models.DateTimeField(verbose_name="set_data", auto_now_add=True)
    owner_id = models.ForeignKey(User, verbose_name="owner", on_delete=models.SET_NULL, related_name="user_chats",
                                 null=True)
    users = models.ManyToManyField(User, verbose_name="users", blank=True)

    class Meta:
        verbose_name = "Chat"
        verbose_name_plural = "Chats"

    def __str__(self):
        return f"{self.id} - name: {self.name}"

    def get_absolute_url(self):
        return reverse('chat_detail', kwargs={'chat_slug': self.slug})


class Message(models.Model):
    """Chat message"""
    message = models.TextField(verbose_name="message", blank=True)
    is_read = models.ManyToManyField(User, verbose_name='is_read')
    pub_date = models.DateTimeField(verbose_name="set_data", auto_now_add=True)
    owner_id = models.ForeignKey(User, verbose_name="owner", on_delete=models.SET_NULL, related_name="user_messages",
                                 null=True, blank=True)
    chat_id = models.ForeignKey(Chat, verbose_name="chat_id", on_delete=models.CASCADE, related_name="chat_messages")

    class Meta:
        ordering = ["-pub_date"]
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"Chat_id: {self.chat_id}- message_id: {self.pk}"

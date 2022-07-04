from django.contrib import admin
from main.models import Chat, Message


@admin.register(Chat)
class AdminChat(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'pub_date')
    list_display_links = ('id', 'name', 'slug')
    fields = ('name', 'slug', 'password', 'owner_id', 'users')
    search_fields = ('name',)
    list_filter = ('name', 'slug', 'pub_date')
    list_max_show_all = 5
    list_per_page = 10
    raw_id_fields = ('users',)
    actions = ['make_private', 'make_open']

    @admin.action(description='Сделать приватным')
    def make_private(self, request, queryset):
        queryset.update(is_password=True)

    @admin.action(description='Сделать открытым')
    def make_open(self, request, queryset):
        queryset.update(is_password=False)


@admin.register(Message)
class AdminMessage(admin.ModelAdmin):
    list_display = ('id', 'message', 'pub_date')
    list_display_links = ('id', 'message')
    fields = ('message', 'owner_id', 'chat_id', 'is_read')
    search_fields = ('message',)
    list_filter = ('message', 'pub_date')
    list_max_show_all = 5
    list_per_page = 10
    raw_id_fields = ('is_read',)
    actions = ['make_read', 'make_unread']

    @admin.action(description='Прочитать сообщения')
    def make_read(self, request, queryset):
        [message.is_read.add(request.user) for message in queryset]

    @admin.action(description='Сделать непрочитаными')
    def make_unread(self, request, queryset):
        [message.is_read.remove(request.user) for message in queryset if message.owner_id_id != request.user.id]

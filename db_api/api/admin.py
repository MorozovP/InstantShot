from django.contrib import admin
from .models import Message, BotUser, BotUserRequest


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'text')
    search_fields = ('name', 'text')


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name')
    search_fields = ('id', 'username')


@admin.register(BotUserRequest)
class BotUserRequestAdmin(admin.ModelAdmin):
    list_display = ('bot_user_id', 'date', 'time', 'requested_url')

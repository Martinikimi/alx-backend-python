from django.contrib import admin
from .models import Message, Notification, MessageHistory

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'timestamp', 'read', 'edited']
    list_filter = ['timestamp', 'read', 'edited']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'timestamp', 'is_read']
    list_filter = ['timestamp', 'is_read']

@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ['message', 'edit_timestamp']
    list_filter = ['edit_timestamp']

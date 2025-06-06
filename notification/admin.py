from django.contrib import admin
from django.contrib.admin import AdminSite
from .models import (
    NotificationEnchaire,
    NotificationDemandeEnchaire,
)

@admin.register(NotificationEnchaire)
class NotificationEnchaireAdmin(admin.ModelAdmin):
    list_display = ('enchaire', 'user', 'message', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('message', 'user__username', 'enchaire__id')

@admin.register(NotificationDemandeEnchaire)
class NotificationDemandeEnchaireAdmin(admin.ModelAdmin):
    list_display = ('enchaire', 'user', 'message', 'link', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('message', 'user__username')



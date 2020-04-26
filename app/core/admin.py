from django.contrib import admin
from core import models


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'name']
    list_display_links = ['email', 'name']
    ordering = ['email']
    search_fields = ['email', 'name']

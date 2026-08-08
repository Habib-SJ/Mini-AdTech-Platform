from django.contrib import admin

# Register your models here.

from .models import Impression, Click



@admin.register(Impression)
class ImpressionAdmin(admin.ModelAdmin):
    list_display = ('ad', 'publisher', 'ip_address', 'user_agent','created_at')

@admin.register(Click)
class ClickAdmin(admin.ModelAdmin):
    list_display = ('ad', 'publisher', 'impression', 'ip_address', 'user_agent','created_at')
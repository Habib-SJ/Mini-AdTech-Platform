from django.contrib import admin

# Register your models here.
from .models import Advertiser, Publisher



@admin.register(Advertiser)
class AdvertiserAdmin(admin.ModelAdmin):
    list_display = ('company', 'brand', 'address', 'category', 'wallet_balance', 'is_active', 'is_valid', 'created_at')


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('website_app_name', 'content_category', 'daily_traffic', 'average_site_speed', 'bank_card_number', 'is_active', 'is_valid', 'created_at')
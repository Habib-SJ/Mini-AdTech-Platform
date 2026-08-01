from django.contrib import admin

# Register your models here.

from .models import Campaign, Ad



@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('advertiser', 'title', 'daily_budget', 'total_budget', 'start_date', 'end_date', 'status', 'created_at')


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'title', 'image', 'destination_url', 'cpc', 'is_active', 'created_at')

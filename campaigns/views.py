from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Campaign
from .services import calculate_ctr

def campaign_ctr_view(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)
    ctr = calculate_ctr(campaign)
    return JsonResponse({
        "campaign_id": campaign.id,
        "campaign_title": campaign.title,
        "ctr": ctr
    })

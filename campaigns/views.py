from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from .models import Campaign
from .serializers import  CTRResponseSerializer,ReportQuerySerializer,CampaignReportSerializer
from .services import (calculate_ctr, get_campaign_report, get_top_campaigns,select_random_ad, NoEligibleAdError,register_click, AdNotActiveError, CampaignNotActiveError,
    CampaignOutOfDateRangeError, InsufficientDailyBudgetError,
    InsufficientTotalBudgetError)
from datetime import datetime
from accounts.models import Publisher
from tracking.models import Impression
from tracking.utils import get_client_ip
from tracking.services import sign_impression_id, unsign_impression_id, ClickTokenTamperedError, ClickTokenExpiredError

@api_view(['GET'])
def campaign_ctr_view(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)
    ctr = calculate_ctr(campaign)
    data = {
        "campaign_id": campaign.id,
        "campaign_title": campaign.title,
        "ctr": ctr
    }
    serializer = CTRResponseSerializer(data)

    return Response(serializer.data)

@api_view(['GET'])
def campaign_report_view(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)

    query_serializer = ReportQuerySerializer(data=request.query_params)
    query_serializer.is_valid(raise_exception=True)

    report_data = get_campaign_report(
        campaign,
        query_serializer.validated_data['start_date'],
        query_serializer.validated_data['end_date']
    )

    output_serializer = CampaignReportSerializer(report_data)


    return Response(output_serializer.data, status=status.HTTP_200_OK)


def campaign_top_view(request):
    limit = request.GET.get('limit', 10)
    order_by = request.GET.get('order_by', 'clicks')

    try:
        limit = int(limit)
    except Exception as e:
        return JsonResponse({"error": "limit must be int"}, status=400)

    if order_by not in ['clicks', 'ctr']:
        return JsonResponse({"error":"order_by must either have the clicks value or ctr value"}, status=400)

    top_campaigns = get_top_campaigns(limit=limit, order_by=order_by)


    results = [
        {
            "id":c.id,
            "title": c.title,
            "click_count": c.click_count,
            "impression_count": getattr(c, 'impression_count', 0),
            "ctr": getattr(c, 'ctr', 0)
        }
        for c in top_campaigns

    ]

    return JsonResponse(results, safe=False)






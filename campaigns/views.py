from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Campaign
from .services import calculate_ctr, get_campaign_report, get_top_campaigns
from datetime import datetime

def campaign_ctr_view(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)
    ctr = calculate_ctr(campaign)
    return JsonResponse({
        "campaign_id": campaign.id,
        "campaign_title": campaign.title,
        "ctr": ctr
    })
class ReportParameterError(Exception):
    pass
class EmptyOrMissingDateParameterError(ReportParameterError): 
    pass
class InvalidDateFormatError(ReportParameterError):
    pass
class InvalidDateRangeError(ReportParameterError):
    pass

def parse_date_range(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if not start_date_str or not end_date_str:
        raise EmptyOrMissingDateParameterError("start_date and end_date are required")

    #print('start and end 1',start_date_str, end_date_str)
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        raise InvalidDateFormatError("dates must be in YYYY-MM-DD format")

    if start_date > end_date:
       raise InvalidDateRangeError("start_date must not be after end_date")

    return start_date, end_date

def campaign_report_view(request, campaign_id):
    campaign = get_object_or_404(Campaign, pk=campaign_id)
    try:
        start_date, end_date = parse_date_range(request)
    except ReportParameterError as e:
        return JsonResponse({"error": str(e)}, status=400)

    report = get_campaign_report(campaign, start_date, end_date)
    

    return JsonResponse(report)


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


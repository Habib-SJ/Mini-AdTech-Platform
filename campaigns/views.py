from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Campaign
from .services import calculate_ctr, get_campaign_report, get_top_campaigns,select_random_ad, NoEligibleAdError
from datetime import datetime
from accounts.models import Publisher
from tracking.models import Impression
from tracking.utils import get_client_ip
from tracking.services import sign_impression_id

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




def serve_ad_view(request, publisher_id):
    # Find the publisher with get_object_or_404
    publisher = get_object_or_404(Publisher, pk=publisher_id)

    # Choose a suitable and active Ad. For the MVP phase, the simplest selection logic: 
    #among all Ads with is_active=True and campaign status='active' and valid in the time frame, 
    #choose one (for now you can choose the first one or a random one — we can add smarter selection logic later)
    try:
        ad = select_random_ad()
    except NoEligibleAdError as e:
        return JsonResponse({"error": str(e)}, status=404)

    # Create an Impression (with ad, publisher, and IP/User-Agent from the request itself)
    impression = Impression.objects.create(
        ad=ad,
        publisher=publisher,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
    )

    # Create a signed token from impression.id
    token = sign_impression_id(impression.id)

    # Return a JSON containing: the ad image, and a click_url containing the signed token
    return JsonResponse({
        "ad_id": ad.id,
        "title": ad.title,
        "destination_url": ad.destination_url,
        "click_url": request.build_absolute_uri(f"/track/click/{token}/"),
    })


from django.shortcuts import render

from django.db import IntegrityError
from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from campaigns.models import Campaign
from campaigns.services import (select_random_ad, NoEligibleAdError,register_click, AdNotActiveError, CampaignNotActiveError,
    CampaignOutOfDateRangeError, InsufficientDailyBudgetError,
    InsufficientTotalBudgetError)
from datetime import datetime
from accounts.models import Publisher
from .models import Impression, Click
from .utils import get_client_ip
from .services import sign_impression_id, unsign_impression_id, ClickTokenTamperedError, ClickTokenExpiredError

# Create your views here.


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




def click_redirect_view(request, token):
    try:
        impression_id = int(unsign_impression_id(token))
    except (ClickTokenTamperedError, ClickTokenExpiredError) as e:
        return JsonResponse({"error": str(e)}, status=400)

    impression = get_object_or_404(Impression, pk=impression_id)
    if Click.objects.filter(impression=impression).exists():
    	return redirect(impression.ad.destination_url)

    try:
        register_click(
            ad=impression.ad,
            publisher=impression.publisher,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            impression=impression,
        )
    except IntegrityError:
        pass
    except (
        AdNotActiveError, CampaignNotActiveError, CampaignOutOfDateRangeError,
        InsufficientDailyBudgetError, InsufficientTotalBudgetError
    ) as e:
        return JsonResponse({"error": str(e)}, status=400)

    return redirect(impression.ad.destination_url)

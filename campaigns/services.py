from django.db.models import Sum, Count, F, ExpressionWrapper, FloatField, Case, When, Value
from django.utils import timezone
from django.db import transaction
from datetime import date

from tracking.models import Click, Impression
from campaigns.models import Campaign, Ad

import random


def get_daily_cpc_consumption(campaign):
	today = timezone.now().date()
	res = Click.objects.filter(created_at__date=today, ad__campaign = campaign).aggregate(daily_cpc=Sum('ad__cpc'))
	return res.get('daily_cpc', 0) or 0

def get_total_cpc_consumption(campaign):
	res = Click.objects.filter(ad__campaign = campaign).aggregate(total_cpc=Sum('ad__cpc'))
	return res.get('total_cpc', 0) or 0
	
# custom exception
class AdNotActiveError(Exception):
    def __init__(self, message="This ad is not active."):
        super().__init__(message)

class CampaignNotActiveError(Exception):
    def __init__(self, message="This campaign is not active."):
        super().__init__(message)

class CampaignOutOfDateRangeError(Exception):
    def __init__(self, message="This campaign is outside its date range."):
        super().__init__(message)

class InsufficientDailyBudgetError(Exception):
    def __init__(self, message="Daily budget exhausted for this campaign."):
        super().__init__(message)

class InsufficientTotalBudgetError(Exception):
    def __init__(self, message="Total budget exhausted for this campaign."):
        super().__init__(message)

class NoEligibleAdError(Exception):
    pass



def close_campaign_if_exhausted(campaign):
    daily_used = get_daily_cpc_consumption(campaign)
    total_used = get_total_cpc_consumption(campaign)
    if daily_used >= campaign.daily_budget or total_used >= campaign.total_budget:
        campaign.status = 'stop'
        campaign.save()

  
def register_click(ad, publisher, ip_address, user_agent, impression=None):
    with transaction.atomic():
        campaign = Campaign.objects.select_for_update().get(pk=ad.campaign.pk)

        if not ad.is_active:
        	raise AdNotActiveError

        if campaign.status in ['stop', 'closed']:
        	raise CampaignNotActiveError

        if timezone.now() < campaign.start_date or timezone.now() > campaign.end_date:
        	raise CampaignOutOfDateRangeError

        if (get_daily_cpc_consumption(campaign) + ad.cpc) > campaign.daily_budget :
        	raise InsufficientDailyBudgetError

        if (get_total_cpc_consumption(campaign) + ad.cpc) > campaign.total_budget :
        	raise InsufficientTotalBudgetError

        click = Click.objects.create(ad = ad, publisher= publisher, ip_address = ip_address, user_agent= user_agent, impression = impression)
        close_campaign_if_exhausted(campaign)

        
        return click

def calculate_ctr(campaign):
    impression_count = Impression.objects.filter(ad__campaign = campaign).count()
    click_count = Click.objects.filter(ad__campaign = campaign).count()

    if impression_count == 0 or not impression_count:
        return None
    ctr = (click_count / impression_count) * 100

    return round (ctr,2)


def get_campaign_report(campaign, start_date, end_date):
    impressions_count = Impression.objects.filter(ad__campaign = campaign, created_at__date__range = [start_date, end_date]).count()
  
    clicks_count     = Click.objects.filter(ad__campaign = campaign, created_at__date__range = [start_date, end_date]).count()

    if impressions_count == 0:
        total_ctr = None
    else:
        total_ctr = round(((clicks_count / impressions_count) * 100), 2)
    
    cpcs = Click.objects.filter(ad__campaign = campaign, created_at__date__range = [start_date, end_date]).aggregate(total_cpcs=Sum('ad__cpc'))

    total_Statistics = {
    'start_date' : start_date,
    'end_date'   : end_date,
    'impressions': impressions_count,
    'clicks'     : clicks_count,     
    'cost'       : round(float(cpcs.get('total_cpcs', 0) or 0), 2), 
    'ctr'        : round(total_ctr, 4) if total_ctr is not None else None
    }

    return total_Statistics




def get_top_campaigns(limit=10, order_by = 'clicks'):
    qs = Campaign.objects.annotate(
    click_count=Count('ad__click', distinct=True),
    impression_count=Count('ad__impression', distinct=True),
    ).annotate(
    ctr=Case(
        When(impression_count = 0, then=Value(0.0)),
        default = 
        ExpressionWrapper(
        F('click_count') * 100.0 / F('impression_count'),
        output_field=FloatField()
    ),
        output_field = FloatField()
    ))
    if order_by == 'ctr':
        qs = qs.order_by('-ctr', '-impression_count')
    else:
        qs = qs.order_by('-click_count')

    return qs[:limit]


def select_random_ad():
    now = timezone.now()
    eligible_ids = list(
        Ad.objects.filter(
            is_active=True,
            campaign__status='active',
            campaign__start_date__lte=now,
            campaign__end_date__gte=now,
        ).values_list('id', flat=True)
    )
    if not eligible_ids:
        raise NoEligibleAdError("No eligible active ad found.")
    
    selected_ad_id = random.choice(eligible_ids)
    
    selected_ad = (
        Ad.objects.select_related('campaign').get(id=selected_ad_id)
        )

    return selected_ad
        








        



    

from django.db.models import Sum
from django.utils import timezone
from django.db import transaction

from tracking.models import Click
from campaigns.models import Campaign


def get_daily_cpc_consumption(campaign):
	today = timezone.now().date()
	res = Click.objects.filter(created_at__date=today, ad__campaign = campaign).aggregate(daily_cpc=Sum('ad__cpc'))
	return res.get('daily_cpc', 0) or 0

def get_total_cpc_consumption(campaign):
	res = Click.objects.filter(ad__campaign = campaign).aggregate(total_cpc=Sum('ad__cpc'))
	return res.get('total_cpc', 0) or 0
	
# custom exception
class AdNotActiveError(Exception): #ad disabled
	pass

class CampaignNotActiveError(Exception): #campaign status not active
	pass
   
class CampaignOutOfDateRangeError(Exception): # date not range
	pass
   
class InsufficientDailyBudgetError(Exception): # finish dayily budget
	pass
  
class InsufficientTotalBudgetError(Exception): # finish month budget
	pass



  
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

        
        return click
        



    

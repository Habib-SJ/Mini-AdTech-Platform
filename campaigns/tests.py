from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model


from django.contrib.auth.models import User
from accounts.models import Advertiser, Publisher
from tracking.models import Click, Impression
from campaigns.models import Campaign, Ad
from campaigns.services import (
    register_click, AdNotActiveError, CampaignNotActiveError,
    CampaignOutOfDateRangeError, InsufficientDailyBudgetError,
    InsufficientTotalBudgetError, calculate_ctr, get_campaign_report,
    get_top_campaigns
)


#################################################################
User = get_user_model()


class RegisterClickTests(TestCase):
    def setUp(self):
        self.adv_user = User.objects.create_user(
            username="adv_user",
            email="advertiser@example.com",
            password="securepassword123",
            first_name="Ali",
            last_name="Ahmadi",
        )
        self.pub_user = User.objects.create_user(
            username = "pub_user",
            email = "publisher@example.com",
            password = "securepassword123",
            first_name = "sara",
            last_name = "Rezaee"

            )
        self.advertiser = Advertiser.objects.create(
            user = self.adv_user,
            company = "nobitex",
            brand = "nobi",
            address = "Tehran bozorg",
            category = "tech",
            wallet_balance = 123456789,
            is_active = True,
            is_valid = True,
            )
        self.publisher = Publisher.objects.create(
            user = self.pub_user,
            website_app_name = "varzesh3",
            content_category = "sport",
            daily_traffic = 1540000,
            average_site_speed = 15,
            bank_card_number = "6037226514259865",
            is_active = True,
            is_valid = True,
            )
        now = timezone.now()
        self.campaign = Campaign.objects.create(
            advertiser = self.advertiser,
            title = "yalda_night",
            daily_budget = 2000,
            total_budget = 5000,
            start_date = now - timedelta(days=1),
            end_date =  now + timedelta(days=5),
            status = "active"
            )

        self.ad = Ad.objects.create(
            campaign = self.campaign,
            title = "yaldaaaa",
            image = "",
            destination_url = "https://www.azki.com/car-insurance/third-party-insurance",
            cpc = 900,
            is_active = True
            )
#################################################################
            #successful_click
#################################################################
    def test_successful_click_creates_record(self):
        click = register_click(
        ad=self.ad,
        publisher=self.publisher,
        ip_address="192.168.1.1",
        user_agent="test-agent",
        impression= None
    )
        self.assertEqual(Click.objects.count(), 1)
#################################################################
            #inactive_ad
#################################################################    
    def test_inactive_ad_raises_error(self):
        now = timezone.now()
        self.campaign = Campaign.objects.create(
            advertiser = self.advertiser,
            title = "yalda_night",
            daily_budget = 2000,
            total_budget = 5000,
            start_date = now - timedelta(days=1),
            end_date =  now + timedelta(days=5),
            status = "active"
            )
        self.ad1 = Ad.objects.create(
            campaign = self.campaign,
            title = "yaldaaaa",
            image = "",
            destination_url = "https://www.azki.com/car-insurance/third-party-insurance",
            cpc = 10000,
            is_active = False
            )
        with self.assertRaises(AdNotActiveError): 
            register_click(
                ad=self.ad1,
                publisher=self.publisher,
                ip_address="192.168.1.1",
                user_agent="test-agent",
                impression= None)
#################################################################
            #stopped_campaign
#################################################################
    def test_stopped_campaign_raises_error(self):
        now = timezone.now()
        self.campaign1 = Campaign.objects.create(
            advertiser = self.advertiser,
            title = "yalda_night",
            daily_budget = 100000000,
            total_budget = 500000000,
            start_date = now - timedelta(days=1),
            end_date =  now + timedelta(days=5),
            status = "stop"
            )
        self.ad2 = Ad.objects.create(
            campaign = self.campaign1,
            title = "yaldaaaa",
            image = "",
            destination_url = "https://www.azki.com/car-insurance/third-party-insurance",
            cpc = 10000,
            is_active = True
            )
        with self.assertRaises(CampaignNotActiveError): 
            register_click(
                ad=self.ad2,
                publisher=self.publisher,
                ip_address="192.168.1.1",
                user_agent="test-agent",
                impression= None)
#################################################################
            #campaign_out_of_date
#################################################################
    def test_campaign_out_of_date_range_raises_error(self):
        now = timezone.now()
        self.campaign2 = Campaign.objects.create(
            advertiser = self.advertiser,
            title = "yalda_night",
            daily_budget = 100000000,
            total_budget = 500000000,
            start_date = now - timedelta(days=7),
            end_date =  now - timedelta(days=2),
            status = "active"
            )
        self.ad3 = Ad.objects.create(
            campaign = self.campaign2,
            title = "yaldaaaa",
            image = "",
            destination_url = "https://www.azki.com/car-insurance/third-party-insurance",
            cpc = 10000,
            is_active = True
            )

        with self.assertRaises(CampaignOutOfDateRangeError): 
            register_click(
                ad=self.ad3,
                publisher=self.publisher,
                ip_address="192.168.1.1",
                user_agent="test-agent",
                impression= None)
#################################################################
            #insufficient_daily_budget
#################################################################
    def test_insufficient_daily_budget_raises_error(self):
        click = register_click(
            ad=self.ad,
            publisher=self.publisher,
            ip_address="192.168.1.1",
            user_agent="test-agent",
            impression= None
        )
        click = register_click(
            ad=self.ad,
            publisher=self.publisher,
            ip_address="192.168.1.1",
            user_agent="test-agent",
            impression= None
    )
        with self.assertRaises(InsufficientDailyBudgetError): 
            register_click(
                ad=self.ad,
                publisher=self.publisher,
                ip_address="192.168.1.1",
                user_agent="test-agent",
                impression= None)
#################################################################
            #insufficient_total_budget
#################################################################
    def test_insufficient_total_budget_raises_error(self):
        now = timezone.now()
        self.campaign3 = Campaign.objects.create(
            advertiser = self.advertiser,
            title = "yalda_night",
            daily_budget = 100000,
            total_budget = 50000,
            start_date = now - timedelta(days=1),
            end_date =  now + timedelta(days=5),
            status = "active"
            )
        self.ad4 = Ad.objects.create(
            campaign = self.campaign3,
            title = "yaldaaaa",
            image = "",
            destination_url = "https://www.azki.com/car-insurance/third-party-insurance",
            cpc = 24000,
            is_active = True
            )

        click = register_click(
            ad=self.ad4,
            publisher=self.publisher,
            ip_address="192.168.1.1",
            user_agent="test-agent",
            impression= None
        )
        click = register_click(
            ad=self.ad4,
            publisher=self.publisher,
            ip_address="192.168.1.1",
            user_agent="test-agent",
            impression= None
    )
        with self.assertRaises(InsufficientTotalBudgetError): 
            register_click(
                ad=self.ad4,
                publisher=self.publisher,
                ip_address="192.168.1.1",
                user_agent="test-agent",
                impression= None)

#################################################################
            #campaign closes when budget exhausted
#################################################################
    def test_campaign_closes_when_budget_exhausted(self):
        now = timezone.now()
        campaign = Campaign.objects.create(
            advertiser=self.advertiser,
            title="auto_close_test_campaign",
            daily_budget=100000,
            total_budget=10000, 
            start_date = now - timedelta(days=1),
            end_date =  now + timedelta(days=5),
            status="active",
        )

        ad = Ad.objects.create(
            campaign=campaign,
            title="auto_close_test_ad",
            destination_url="https://example.com",
            cpc=10000,
            is_active=True,
        )

    
        click = register_click(
            ad=ad,
            publisher=self.publisher,
            ip_address="1.1.1.1",
            user_agent="Mozilla/5.0",
            impression=None,
        )

        self.assertIsNotNone(click)

        campaign.refresh_from_db()

        self.assertEqual(campaign.status, "stop")

#################################################################
#################################################################

class BaseAdTechTest(TestCase):
    @classmethod
    def setUpTestData(cls):
       
        cls.adv_user = User.objects.create_user(
            username="adv_user",
            email="advertiser@example.com",
            password="securepassword123",
            first_name="Ali",
            last_name="Ahmadi",
        )
        cls.pub_user = User.objects.create_user(
            username = "pub_user",
            email = "publisher@example.com",
            password = "securepassword123",
            first_name = "sara",
            last_name = "Rezaee"

            )
        cls.advertiser = Advertiser.objects.create(
            user = cls.adv_user,
            company = "nobitex",
            brand = "nobi",
            address = "Tehran bozorg",
            category = "tech",
            wallet_balance = 123456789,
            is_active = True,
            is_valid = True,
            )
        cls.publisher = Publisher.objects.create(
            user = cls.pub_user,
            website_app_name = "varzesh3",
            content_category = "sport",
            daily_traffic = 1540000,
            average_site_speed = 15,
            bank_card_number = "6037226514259865",
            is_active = True,
            is_valid = True,
            )
        now = timezone.now()
        cls.campaign = Campaign.objects.create(
            advertiser = cls.advertiser,
            title = "yalda_night",
            daily_budget = 2000,
            total_budget = 5000,
            start_date = now - timedelta(days=1),
            end_date =  now + timedelta(days=5),
            status = "active"
            )
        cls.campaign0 = Campaign.objects.create(
            advertiser = cls.advertiser,
            title = "yalda_night0",
            daily_budget = 2000,
            total_budget = 5000,
            start_date = now - timedelta(days=1),
            end_date =  now + timedelta(days=5),
            status = "active"
            )

        cls.campaign2 = Campaign.objects.create(
            advertiser=cls.advertiser,
            title="campaign_no_activity",
            daily_budget=2000,
            total_budget=5000,
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=5),
            status="active"
        )
        cls.adcamp = Ad.objects.create(
            campaign = cls.campaign,
            title = "yaldaaaa",
            image = "",
            destination_url="https://www.azki.com/car-insurance/third-party-insurance",
            cpc = 900,
            is_active = True
            )
        cls.adcamp2 = Ad.objects.create(
            campaign = cls.campaign,
            title = "norooz",
            image = "",
            destination_url = "https://www.basalam.com/car-insurance/third-party-insurance",
            cpc = 900,
            is_active = True
            )

        cls.adcamp0 = Ad.objects.create(
            campaign = cls.campaign0,
            title = "norooz",
            image = "",
            destination_url = "https://www.basalam.com/car-insurance/third-party-insurance",
            cpc = 900,
            is_active = True
            )

        cls.impression1 = Impression.objects.create(
            ad = cls.adcamp,
            publisher = cls.publisher,
            ip_address = '192.168.1.23',
            user_agent = "saklhklj lkasjdfh kldsh iwero s lsd lasdh lksdh lierowier ",
            )
        cls.impression2 = Impression.objects.create(
            ad = cls.adcamp,
            publisher = cls.publisher,
            ip_address = '192.168.1.23',
            user_agent = "saklhklj lkasjdfh kldsh iwero s lsd lasdh lksdh lierowier ",
            )
        Impression.objects.filter(pk=cls.impression2.pk).update(
            created_at=timezone.now() - timedelta(days=3)
            )
        cls.click1 = Click.objects.create(
            ad = cls.adcamp,
            publisher = cls.publisher,
            impression = cls.impression1,
            ip_address = '45.15.78.32',
            user_agent = "slkdjf ;lswpoeowieasdl ncljds;lj aoweuwwesd;lkjdl;jdkfqwwpoeirsdjfl nc jl;a"

            )
        cls.click2 = Click.objects.create(
            ad = cls.adcamp,
            publisher = cls.publisher,
            impression = cls.impression2,
            ip_address = '45.15.78.32',
            user_agent = "slkdjf ;lswpoeowieasdl ncljds;lj aoweuwwesd;lkjdl;jdkfqwwpoeirsdjfl nc jl;a"

            )
        Click.objects.filter(pk=cls.click2.pk).update(
            created_at=timezone.now() - timedelta(days=3)
            )        
        cls.click3 = Click.objects.create(
            ad = cls.adcamp0,
            publisher = cls.publisher,
            #impression = '',
            ip_address = '45.15.78.32',
            user_agent = "slkdjf ;lswpoeowieasdl ncljds;lj aoweuwwesd;lkjdl;jdkfqwwpoeirsdjfl nc jl;a"

            )



class ReportCampaignTests(BaseAdTechTest):
    #def setUp(self):


#################################################################
            #ctr-test
#################################################################
    def test_calculate_ctr_with_valid_data(self):
        ctr = calculate_ctr(
        campaign=self.campaign
    )

        self.assertEqual(ctr, 100)
#################################################################
    def test_calculate_ctr_with_invalid_data(self):
        ctr = calculate_ctr(
        campaign=self.campaign0
    )

        self.assertEqual(ctr, None)

#################################################################
            #campaign-report-test
#################################################################
    def test_get_daily_report_with_valid_data(self):
        now = timezone.now().date()
        start_date = now #- timedelta(days=1)
        end_date = now #- timedelta(days=1)

        report = get_campaign_report(
            campaign = self.campaign,
            start_date = start_date,
            end_date = end_date)
        self.assertEqual(report['start_date'], start_date)
        self.assertEqual(report['end_date'], end_date)
        self.assertEqual(report['impressions'], 1)
        self.assertEqual(report['clicks'], 1)
        self.assertEqual(report['cost'], 900)
        self.assertEqual(report['ctr'], 100)
#################################################################
    def test_get_multi_day_rangereport_with_valid_data(self):
        now = timezone.now().date()
        start_date = now - timedelta(days=4)
        end_date = now + timedelta(days=5)

        report = get_campaign_report(
            campaign = self.campaign,
            start_date = start_date,
            end_date = end_date)
        self.assertEqual(report['start_date'], start_date)
        self.assertEqual(report['end_date'], end_date)
        self.assertEqual(report['impressions'], 2)
        self.assertEqual(report['clicks'], 2)
        self.assertEqual(report['cost'], 1800)
        self.assertEqual(report['ctr'], 100)    
#################################################################
    def test_get_multi_day_rangereport_with_out_data(self):
        now = timezone.now().date()
        start_date = now - timedelta(days=6)
        end_date = now - timedelta(days=4)

        report = get_campaign_report(
            campaign = self.campaign,
            start_date = start_date,
            end_date = end_date)
        self.assertEqual(report['start_date'], start_date)
        self.assertEqual(report['end_date'], end_date)
        self.assertEqual(report['impressions'], 0)
        self.assertEqual(report['clicks'], 0)
        self.assertEqual(report['cost'], 0)
        self.assertEqual(report['ctr'], None)  

#################################################################
            #top-campaigns
#################################################################
    def test_get_top_campaigns_order_by_clicks(self):
        result = list(get_top_campaigns(limit=10, order_by='clicks'))

        self.assertEqual(result[0], self.campaign)
        self.assertEqual(result[0].click_count, 2)
        self.assertEqual(result[0].impression_count, 2)
#################################################################
    def test_get_top_campaigns_order_by_ctr(self):
        result = list(get_top_campaigns(limit=10, order_by='ctr'))

        self.assertEqual(result[0], self.campaign)
        self.assertEqual(result[-1], self.campaign2)
#################################################################
    def test_get_top_campaigns_respects_limit(self):
        result = list(get_top_campaigns(limit=1, order_by='clicks'))

        self.assertEqual(len(result), 1)
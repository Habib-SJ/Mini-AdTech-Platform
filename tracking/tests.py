from django.test import TestCase
#from django.utils import timezone
#from datetime import timedelta
from django.contrib.auth import get_user_model
#from django.core.signing import TimestampSigner, BadSignature, SignatureExpired

from django.test import SimpleTestCase
from tracking.services import (
    sign_impression_id, unsign_impression_id,
    ClickTokenExpiredError, ClickTokenTamperedError,
)


from .models import Click, Impression

#from .views import serve_ad_view#, click_redirect_view

from campaigns.tests import BaseAdTechTest
from campaigns.models import Ad, Campaign

from accounts.models import Publisher





#################################################################



class Report_AD_Redirect_View_Tests(BaseAdTechTest):


    def test_serve_ad_view_successful(self):
        #publisher1 = self.publisher
        imp_cnt = Impression.objects.count()
        #print(Impression.objects.all())
        response = self.client.get(f'/serve/{self.publisher.id}/')
        data = response.json()
        #print('data', data['click_url'])
        #print('all', Impression.objects.all()[-1])
        token_url = data['click_url'].strip('/').split('/')[-1]
        #print('t_u', token_url)
        last_impression_id = Impression.objects.order_by('-id').first().id
        unsign_impression_ids = unsign_impression_id(token_url)
        #print('l_i', last_impression)
        #print('t=l', unsign_impression_id(token_url))
        self.assertEqual(response.status_code, 200)
        self.assertIn('click_url', data)
        #print(type(last_impression_id), last_impression_id)
        #print(type(unsign_impression_ids), unsign_impression_ids)
        #print(last_impression_id, unsign_impression_ids)
        #self.assertIn(last_impression_id, unsign_impression_ids)
        self.assertIn(str(last_impression_id), unsign_impression_ids)

        self.assertEqual(Impression.objects.count(), imp_cnt + 1)
    def test_serve_ad_view_invalid_publisher(self):
        pID = 999999
        response = self.client.get(f'/serve/{pID}/')
        #data = response.json()
        self.assertEqual(response.status_code, 404)  

    def test_404_body_is_consistent(self):
        Publisher.objects.update(is_valid=False)
        blocked = self.client.get(f'/serve/{self.publisher.id}/')
        missing = self.client.get('/serve/999999/')
        self.assertEqual(blocked.status_code, missing.status_code)
        self.assertEqual(blocked.content, missing.content)

    def test_serve_ad_view_invalid_Ads(self):
        Ad.objects.update(is_active=False)  
        response = self.client.get(f'/serve/{self.publisher.id}/')
        self.assertEqual(response.status_code, 404, msg=f"There are no valid and active ads.Response content: {response.content.decode()}")

    def test_serve_ad_view_is_active_false(self):
        Publisher.objects.update(is_active=False)  
        imp_cnt = Impression.objects.count()
        #print(Impression.objects.all())
        response = self.client.get(f'/serve/{self.publisher.id}/')

        self.assertEqual(response.status_code, 404) 
        self.assertEqual(Impression.objects.count(), imp_cnt)
        
    def test_serve_ad_view_is_valid_false(self):
        Publisher.objects.update(is_valid=False)  
        imp_cnt = Impression.objects.count()
        #print(Impression.objects.all())
        response = self.client.get(f'/serve/{self.publisher.id}/')

        self.assertEqual(response.status_code, 404) 
        self.assertEqual(Impression.objects.count(), imp_cnt)
        

#################################################
#################################################
    def test_click_redirect_view_successful(self):
        Ad.objects.update(is_active=True) 
        initial_click_count = Click.objects.count()
        #print('icc', initial_click_count)

        response  = self.client.get(f'/serve/{self.publisher.id}/')
        data      = response.json()
        click_url = data['click_url']
        destination_url = data['destination_url']

        #print(data)
        redirect_response = self.client.get(click_url)
        self.assertEqual(redirect_response.status_code, 302)

        self.assertEqual(redirect_response.url, destination_url)        

        self.assertEqual(Click.objects.count(), initial_click_count+1, msg="A new click record was created in the database.")
        
    def test_click_redirect_view_duplicated_click(self):
        response = self.client.get(f'/serve/{self.publisher.id}/')
        click_url = response.json()['click_url']
        initial_click_count = Click.objects.count()

        first = self.client.get(click_url)
        second = self.client.get(click_url)

        self.assertEqual(first.status_code, 302)
        self.assertEqual(second.status_code, 302)
        self.assertEqual(Click.objects.count(), initial_click_count + 1)

    def test_click_redirect_view_tampered_token(self):
        Ad.objects.update(is_active=True)
        response = self.client.get(f'/serve/{self.publisher.id}/')
        click_url = response.json()['click_url']
        token_url = click_url.rstrip('/') + 'XX/'
        initial_click_count = Click.objects.count()

        redirect_response = self.client.get(token_url)
        #print(redirect_response.status_code)
        self.assertEqual(redirect_response.status_code, 400)
        #print(Click.objects.count(), initial_click_count)
        #self.assertEqual(Click.objects.count(), initial_click_count, msg="The number of clicks did not add up.")

    def test_click_redirect_view_stopped_campaign(self):
        response  = self.client.get(f'/serve/{self.publisher.id}/')
        data      = response.json()
        click_url = data['click_url']

        Campaign.objects.update(status='stop')
        initial_click_count = Click.objects.count()


        redirect_response = self.client.get(click_url)

        #print(data)
        self.assertEqual(Click.objects.count(), initial_click_count)
        self.assertEqual(redirect_response.status_code, 400)

#################################################
#################################################
class ImpressionTokenTests(SimpleTestCase):
    def test_roundtrip_returns_original_id_as_string(self):
        token = sign_impression_id(42)
        self.assertEqual(unsign_impression_id(token), "42")

    def test_expired_token_raises_expired_error(self):
        token = sign_impression_id(42)
        with self.assertRaises(ClickTokenExpiredError):
            unsign_impression_id(token, max_age_seconds=-1)

    def test_tampered_token_raises_tampered_error(self):
        token = sign_impression_id(42)
        with self.assertRaises(ClickTokenTamperedError):
            unsign_impression_id(token + "x")










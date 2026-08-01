from django.db import models
from django.contrib.auth.models import User

class Advertiser(models.Model):
	INDUSTRY_CHOICES = [
    ('insurance', 'Insurance'),
    ('ecommerce', 'E-commerce'),
    ('tech', 'Technology'),
    ('tourism', 'Tourism & Hospitality'),
    ('logistics', 'Transportation & Logistics'),
    ('retail', 'Retail'),
    ('finance', 'Banking & Finance'),    
]

	user = models.OneToOneField(User, on_delete= models.CASCADE)
	company = models.CharField(max_length=100)
	brand = models.CharField(max_length=100)
	address = models.TextField()
	category = models.CharField(max_length=50, choices=INDUSTRY_CHOICES)
	wallet_balance = models.DecimalField(max_digits=12, decimal_places=2)
	is_active = models.BooleanField(default=True)
	is_valid = models.BooleanField(default=True) 
	created_at = models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return self.company



class Publisher(models.Model):
	CONTENT_CATEGORY_CHOICES = [
    ('sport', 'Sport'),
    ('news', 'News'),
    ('tech', 'Technology'),
    ('entertainment', 'Entertainment'),
   
]
	user = models.OneToOneField(User, on_delete= models.CASCADE)
	website_app_name = models.CharField(max_length=100)
	content_category = models.CharField(max_length=50, choices=CONTENT_CATEGORY_CHOICES)
	daily_traffic = models.BigIntegerField()
	average_site_speed = models.DecimalField(max_digits=5, decimal_places=2)
	bank_card_number = models.CharField(max_length=16)
	is_active = models.BooleanField(default=True)
	is_valid = models.BooleanField(default=True) 
	created_at = models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return self.website_app_name




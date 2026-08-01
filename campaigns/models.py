from django.db import models
from accounts.models import Advertiser, Publisher
# Create your models here.



class Campaign(models.Model):
	STATUS_CHOICES = [
    ('active', 'Active'),
    ('stop', 'Stop'),
    ('closed', 'Closed'),
 
]

	advertiser = models.ForeignKey(Advertiser, on_delete= models.CASCADE)
	title = models.CharField(max_length=100)
	daily_budget = models.DecimalField(max_digits=12, decimal_places=2)
	total_budget = models.DecimalField(max_digits=12, decimal_places=2)
	start_date = models.DateTimeField()
	end_date = models.DateTimeField()
	status = models.CharField(max_length=50, choices=STATUS_CHOICES)
	created_at = models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return self.title



class Ad(models.Model):
	campaign = models.ForeignKey(Campaign, on_delete= models.CASCADE)
	title = models.CharField(max_length=100)
	image = models.ImageField()
	destination_url = models.URLField(max_length=500)
	cpc = models.DecimalField(max_digits=12, decimal_places=2)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return self.title





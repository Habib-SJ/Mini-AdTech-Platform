from django.db import models
from accounts.models import Publisher
from campaigns.models import Ad
# Create your models here.



class Impression(models.Model):
	ad = models.ForeignKey(Ad, on_delete= models.CASCADE)
	publisher = models.ForeignKey(Publisher, on_delete= models.CASCADE)
	ip_address = models.GenericIPAddressField()
	user_agent = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return self.ip_address


class Click(models.Model):
	ad = models.ForeignKey(Ad, on_delete= models.CASCADE)
	publisher = models.ForeignKey(Publisher, on_delete= models.CASCADE)
	impression = models.ForeignKey(Impression, on_delete= models.CASCADE, null=True, blank=True)
	ip_address = models.GenericIPAddressField()
	user_agent = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)


	def __str__(self):
		return self.ip_address


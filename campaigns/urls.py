from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    path('campaigns/<int:campaign_id>/ctr/', views.campaign_ctr_view, name='campaign-ctr'),
]
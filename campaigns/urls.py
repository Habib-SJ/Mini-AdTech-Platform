from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    path('campaigns/<int:campaign_id>/ctr/', views.campaign_ctr_view, name='campaign-ctr'),
    path('campaigns/<int:campaign_id>/report/', views.campaign_report_view, name='campaign-report'),
    path('campaigns/top/', views.campaign_top_view, name='campaign-top')
    

]
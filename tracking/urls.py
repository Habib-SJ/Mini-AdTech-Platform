from django.urls import path
from . import views


app_name = 'tracking'

urlpatterns = [
    path('serve/<int:publisher_id>/', views.serve_ad_view, name='serve-ad'),
    path('track/click/<str:token>/', views.click_redirect_view, name='click_redirect')

]
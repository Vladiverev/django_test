from django.urls import path
from . import views as trend_views

urlpatterns = [
    path('', trend_views.home_page, name='home'),
    path('trend/', trend_views.trend, name='trend')
]

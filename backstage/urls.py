from django.urls import path, include
from .views import *

app_name = 'backstage'


urlpatterns = [
    path('index/', index, name='index'),
    path('administrators/', Administrators.as_view(), name='administrators'),
    path('common/', Common.as_view(), name='common'),
    path('getOrdersInfo/', OrdersInfo.as_view(), name='getOrderInfo'),
]

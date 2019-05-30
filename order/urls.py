from django.urls import path
from order import views


app_name = 'order'

urlpatterns = [
    path('create/', views.create, name='create_order'),
    path('unpay/', views.unpay, name='unpay_order'),
    path('unpack/', views.unpack, name='unpack_order'),
    path('untoken/', views.untoken, name='untoken_order'),
    path('finished/', views.finished, name='finished_order'),
    path('cancel/', views.cancel, name='cancel_order'),
    path('distribution/', views.distribution, name='distribution_order'),
    path('confirm/', views.Confirm.as_view(), name='confirm_order'),
    path('online_pay/', views.online_payment, name='online_pay'),
    path('confirm_pay', views.check, name='check'),
    path('check_pay/', views.check_pay, name='check_pay'),
]

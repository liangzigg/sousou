from django.urls import path
from user import views

app_name = 'user'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('address/', views.address, name='address'),
    path('address/query', views.address_query, name='address_query'),
    path('wallet/', views.wallet, name='wallet'),
    path('query_refund/', views.query_refund, name='query_refund'),
    path('delete_address/', views.delete_address, name='delete_address'),
]

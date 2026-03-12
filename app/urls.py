from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
 
urlpatterns = [
     path("", views.home, name = "new_customer"),
     path("regcustomer/", views.regcustomer, name = "reg_customer"),
     path("geninvoice/", views.generate_invoice, name="generate_invoice"),
   
     path('invoice/<int:pk>/', views.view_invoice, name="view_invoice"),
     path('search-customer/', views.search_customer, name='search_customer'),
     path('whatsapp/webhook/', views.whatsapp_webhook, name='whatsapp_webhook'),
 ]+ static( settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

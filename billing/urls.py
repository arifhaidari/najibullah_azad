from django.urls import path
from .views import OrderSummary

app_name = 'billing'

urlpatterns = [
     path('summary/<order_id>',OrderSummary.as_view() , name='order_summary'),
]
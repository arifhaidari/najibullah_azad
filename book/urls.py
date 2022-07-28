import imp
from django.urls import path
from .views import BookDetail, Books

app_name = 'book'

urlpatterns = [
     path('', Books.as_view(), name='list'),
     path('detail/<slug>/', BookDetail.as_view(), name='detail'),
]



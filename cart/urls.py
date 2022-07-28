from django.urls import path
from .views import CartItemList, cart_update, clear_cart, Checkout

app_name = 'cart'


urlpatterns = [
     path('', CartItemList.as_view(), name='cart_home'),
     path('update/', cart_update, name='update_cart'),
     path('clear/', clear_cart, name='clear_cart'),
     path('checkout/', Checkout.as_view(), name='checkout'),
]
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from cart.models import Cart
from order.models import Order


class OrderSummary(View):
     template_name = 'billing/order_summary.html'
     
     def get(self, request , *args, **kwargs):
          is_error = False
          order_object = None
          print('value of kwargs')
          print(kwargs)
          order_id = kwargs['order_id']
         
          try:
               order_object = Order.objects.get(order_id=order_id)
               cart_obj, new_obj = Cart.objects.new_or_get(request)
               the_data = {
                    'cart_obj': cart_obj,
                    'order_object': order_object,
               }
          except:
               messages.error(request, 'Unknown Error Occured. Please try again')
               is_error = True
          
          return render(request, self.template_name, the_data) if not is_error else redirect('cart:item_list')
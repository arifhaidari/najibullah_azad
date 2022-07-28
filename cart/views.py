from decimal import Decimal
from operator import is_not
from django import views
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import View, DetailView
from django.db.models import Q
from django.contrib import messages
from billing.models import BillingProfile
from book.models import Book, BookTypePrice
from .models import Cart, CartBook
from customer.models import Address, Customer
from order.models import Order, ShipmentMethod



class Checkout(View):
     template_name = 'cart/checkout.html'
     
     def get(self, request, *args, **kwargs):
          cart_obj, new_obj = Cart.objects.new_or_get(request)
          if len(cart_obj.cartbook_set.all()) == 0:
               return redirect('cart:cart_home')
          return render(request, self.template_name, {'cart_obj': cart_obj})
     
     def post(self, request, *args, **kwargs):
          print('value of request in post')
          raw_data = request.POST
          print(request.POST)
          cart_obj, new_obj = Cart.objects.new_or_get(request)

          # //
          # billing_address_select = raw_data.get('billing_address_select', None)
          # shipping_address_select = raw_data.get('shipping_address_select', None)
          order_note = raw_data.get('order_note', None)
          is_shipping = raw_data.get('shipping', None)
          billing_phone = raw_data.get('billing_phone', None)
          billing_email = raw_data.get('billing_email', None)
          billing_full_name = raw_data.get('billing_full_name', None)
          
          # create customer
          customer_object, created = Customer.objects.get_or_create(name=billing_full_name, phone=billing_phone, email=billing_email)
          
          # create billing profile
          billing_profile_object, created = BillingProfile.objects.get_or_create(customer=customer_object)
         
          final_order_object = None
          the_type = 'both'
          billing_address_obj = get_create_address(the_type, raw_data, billing_profile_object)
          if billing_address_obj is None:
               messages.error(request, 'Enter billing address information properly')
               return render(request, self.template_name, {'cart_obj': cart_obj})
          if is_shipping is not None and is_shipping == 'on':
               # the_type = 'billing'
               shipping_address_obj = get_create_address('shipping', raw_data, billing_profile_object)
               if shipping_address_obj is None:
                    messages.error(request, 'Enter shipping address information properly')
                    return render(request, self.template_name, {'cart_obj': cart_obj})
               else:
                    order_object = place_order(order_note, billing_address_obj, cart_obj, billing_profile_object)
                    if order_object is None:
                         messages.error(request, 'Uknonwn Error Occured. Please try again')
                         return render(request, self.template_name, {'cart_obj': cart_obj})
                    order_object.shipping_address = shipping_address_obj
                    order_object.save()
                    final_order_object = order_object
          else:
               place_order_obj = place_order(order_note, billing_address_obj, cart_obj, billing_profile_object)
               if place_order_obj is None:
                    messages.error(request, 'Uknonwn Error Occured. Please try again')
                    return render(request, self.template_name, {'cart_obj': cart_obj})
               final_order_object = place_order_obj
          # messages.success(request, 'Order placed successfully')
          if final_order_object is None:
               messages.error(request, 'Unknown Error Occured')
          return redirect('billing:order_summary', order_id=final_order_object.order_id) if final_order_object is not None else render(request, self.template_name, {'cart_obj': cart_obj})
          # return render(request, self.template_name, {'cart_obj': cart_obj})


# maybe place order after successing the payemnt or just mark it as paid after success
def place_order(order_note, address_object, cart_object, billing_profile_object):
     if address_object is None or cart_object is None:
          return None
     order_obj, created = Order.objects.get_or_create(
          cart=cart_object, billing_profile=billing_profile_object,
          active=True, status=Order.OrderStatus.Created
     )
     order_obj.order_note=order_note if order_note is not None and order_note != '' else None
     order_obj.billing_address=address_object
     order_obj.save()
     # delelte previous Orders if there is any --> incomplete orders 
     Order.objects.filter(billing_profile=billing_profile_object, status=Order.OrderStatus.Created).exclude(cart=cart_object).delete()
     return order_obj
     

address_type_dict = {
     'billing': 'Billing',
     'shipping': 'Shipping',
     'both': 'Both',
}


def get_create_address(raw_type, raw_data, billing_profile_object):
     print('inside the get_create_address')
     print(raw_type)
     if raw_type == 'both':
          the_type = 'billing'
     else:
          the_type = raw_type
     full_name = raw_data.get(f"{the_type}_full_name", None)
     country = raw_data.get(f"{the_type}_country", None)
     city = raw_data.get(f"{the_type}_city", None)
     district = raw_data.get(f"{the_type}_district", None)
     zipcode = raw_data.get(f"{the_type}_zipcode", None)
     street = raw_data.get(f"{the_type}_street", None)
     apartment = raw_data.get(f"{the_type}_apartment", None)
     phone = raw_data.get(f"{the_type}_phone", None)
     email = raw_data.get(f"{the_type}_email", None)
     is_not_valid = (full_name == '' or country == '' or city == '' or district == '' 
                 or zipcode == '' or street == '' or phone == '' or email == '')
     if is_not_valid:
          return None
     # first create a billing_profile if not created
     address_object, created = Address.objects.get_or_create(
          billing_profile=billing_profile_object, full_name=full_name, 
          country=country, city=city, district=district, phone=phone,
          apartment= apartment if apartment != '' else None,
          street=street, email=email, zipcode=zipcode
     )
     address_object.address_type=address_type_dict[the_type]
     address_object.save()
     return address_object


def clear_cart(request):
     response_data = {
               "is_error": True,
               }
     if request.method == 'POST':
          cart_obj, new_obj = Cart.objects.new_or_get(request)
          if cart_obj is not None:
               CartBook.objects.filter(cart=cart_obj).delete()
               cart_obj.shipment_fee = 0
               cart_obj.save()
               response_data['is_error'] = False
     return JsonResponse(response_data)


class CartItemList(View):
     template_name = 'cart/cart_home.html'
     # model = CartProduct
     
     def the_data(self, request):
          cart_obj, new_obj = Cart.objects.new_or_get(request)
          cart_items = CartBook.objects.filter(cart=cart_obj).order_by('-id')
          print('value fo cart_obj')
          print(cart_obj.shipment_fee)
          request.session['cart_items'] = cart_obj.current_item_num
          # cart_data = get_cart_brief_items(request)
          shipment_method_list = ShipmentMethod.objects.order_by('-id')
          is_media = False
          is_not_media = False
          for bool in cart_obj.cartbook_set.all():
               if bool.book_type_price.is_media:
                    is_media = True
               else:
                    is_not_media = True   
                    
          print('value fo media or not media')
          print(is_not_media)
          print(is_media)
          context = {
               'object_list': cart_items,
               'cart_obj': cart_obj,
               'shipment_method_list': shipment_method_list,
               'is_media': is_media,
               'is_not_media': is_not_media,
          }
          return context
     
     
     def get(self, request, *args, **kwargs):
          print('insid eth self.the_data(self.request)')
          # print(self.the_data(self.request))
          context = self.the_data(request)
          return render(request, self.template_name, context)
     
     def post(self, request, *args, **kwargs):
          # context = self.the_data(self.request)
          print('value fo request------')
          print(request.POST)
          is_media = False
          if request.method == 'POST':
               selected_fee = request.POST.get('select_shipment_fee', None)
               is_media = selected_fee = '' or selected_fee is None
               try:
                    if not is_media:
                         the_fee = Decimal(selected_fee) 
                         cart_obj, new_obj = Cart.objects.new_or_get(request)
                         cart_obj.shipment_fee = the_fee
                         cart_obj.save()
                         return redirect('cart:checkout')
               except Exception as e:
                    print('value of e')
                    print(e)
          
          return render(request, self.template_name, self.the_data(self.request))


def cart_update(request):
     print('value fo request.POST')
     print(request.POST)
     book_id = request.POST.get('book_id', None)
     operation = request.POST.get('operation', None)
     book_type_id = request.POST.get('book_type_id', None)
     location = request.POST.get('location', None)
     # the_quantity = int(quantity) or 1
     response_data = {
          "is_error": False,
          "is_new_product": False,
          "quantity": 0,
          }
     try:
          book_obj = Book.objects.get(id=book_id)
          book_type_price_obj = BookTypePrice.objects.get(id=book_type_id)
          print('vaue fo book_type_price_obj')
          print(book_type_price_obj)
          cart_obj, new_obj = Cart.objects.new_or_get(request)
          if cart_obj is not None:
               the_filter = Q(Q(book=book_obj) & Q(cart=cart_obj))
               if book_type_id is not None and book_type_id != '':
                    the_filter = the_filter.add(Q(book_type_price__id=book_type_id), Q.AND)
               cart_book_obj_raw = CartBook.objects.filter(the_filter)
               if cart_book_obj_raw.exists():
                    cart_book = cart_book_obj_raw.first()
                    if operation == 'add':
                         print('add up the quantity ')
                         cart_book.book_quantity += 1
                    else:
                         print('minus down the quantity ')
                         if cart_book.book_quantity > 1:
                              cart_book.book_quantity -= 1
                    cart_book.save()
               else:
                    print('create new ---======')
                    try:
                         cart_book = CartBook.objects.create(
                              cart= cart_obj, book=book_obj, book_type_price=book_type_price_obj, book_quantity=1,
                              book_price= book_type_price_obj.price or 0, book_purchase_price=book_type_price_obj.purchase_price or 0
                         )
                         response_data['is_new_product'] = True
                    except:
                         print('erorr occured in creating new one')
                         pass
               # the_dic = update_cart_front_end(response_data, cart_obj, request, cart_product)
               # response_data = {**response_data, **the_dic}
               item_count = cart_obj.current_item_num
               response_data['quantity'] = item_count
               request.session['cart_items'] = item_count
               if location == 'cart_home':
                    response_data['subtotal_item_price'] = cart_book.subtotal_price or 0,
                    response_data['subtotal'] = cart_obj.subtotal,
                    response_data['shipment_fee'] = cart_obj.shipment_fee,
                    response_data['total'] = cart_obj.total,
                    
          else:
               print('cart_obj is not so check it out')
     except Exception as e:
          print('error happened in the exception e')
          print(e)
          response_data['is_error'] = True
     
     return JsonResponse(response_data, status=200)

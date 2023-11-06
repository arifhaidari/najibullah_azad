from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, View
from book.models import Book
from cart.models import Cart, CartBook

class Home(View):
     template_name = 'home/home_page.html'
     
     def get(self, request, *args, **kwargs):
          books = Book.objects.all()
          print('value fo books')
          print(len(books))
          return render(request, self.template_name, {'books': books})


class About(View):
     template_name = 'home/about.html'
     
     def get(self, request, *args, **kwargs):
          return render(request, self.template_name, {})
        
     

class Contact(View):
     template_name = 'home/contact.html'
     
     def get(self, request, *args, **kwargs):
          return render(request, self.template_name, {})   


class Privacy(View):
     template_name = 'home/privacy.html'
     
     def get(self, request, *args, **kwargs):
          return render(request, self.template_name, {})  


def global_item_deleter(request, *args, **kwargs):
     if request.method == "POST":
          print('valeu of request.POST')
          # newsletter_type
          print(request.POST)
          the_id = request.POST.get('the_id', None)
          operation =  request.POST.get('operation', None)
          if the_id is None or operation is None:
               return JsonResponse({'is_error': True})
          data_dict = {"is_error": False }
          
          if operation == 'remove_cart_item':
               try:
                    CartBook.objects.get(id=the_id).delete()
                    cart_obj, new_obj = Cart.objects.new_or_get(request)
                    data_dict['subtotal'] = cart_obj.subtotal,
                    data_dict['shipment_fee'] = cart_obj.shipment_fee,
                    data_dict['current_item_num'] = cart_obj.current_item_num,
                    data_dict['total'] = cart_obj.total,
               except:
                   data_dict['is_error'] = True
          else:
               data_dict['is_error'] = True
          return JsonResponse(data_dict)



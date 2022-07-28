# from decimal import Decimal
from django.db import models
# from django.db.models.signals import pre_save, post_save, m2m_changed
from django.db.models import Sum
from book.models import Book, BookTypePrice
from django.dispatch import receiver

from customer.models import Customer


class CartManager(models.Manager):
     def new_or_get(self, request, the_cart_id=None, the_user=None):
          try:
               print('inside the new_or_get')
               cart_id = request.session.get("cart_id", None)
               print('value fo cart_id')
               print(cart_id)
               if the_cart_id is not None:
                    cart_id = the_cart_id
               qs = self.get_queryset().filter(id=cart_id, is_checked_out=False)
               if qs.count() != 0 and cart_id is not None:
                    new_obj = False
                    cart_obj = qs.first()
               else:
                    print('new cart is crated')
                    cart_obj = self.model.objects.create(customer=None)
                    new_obj = True
                    request.session['cart_id'] = cart_obj.id
          except Exception as e:
               print('value of error in new_or_get')
               print(e)
               cart_obj, new_obj = None, False
          return cart_obj, new_obj
     


class Cart(models.Model):
     customer  = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL)
     shipment_fee = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
     is_checked_out = models.BooleanField(default=False)
     updated_at     = models.DateTimeField(auto_now=True)
     timestamp   = models.DateTimeField(auto_now_add=True)

     objects = CartManager()

     def __str__(self):
          return str(self.timestamp)
     
     @property
     def current_item_num(self):
          if len(self.cartbook_set.all()) != 0:
               total = self.cartbook_set.aggregate(Sum('book_quantity'))
               return total['book_quantity__sum'] or 0
          return 0
     
     @property
     def purchase_price_total(self):
          result = 0
          if len(self.cartbook_set.all()) != 0:
               for item in self.cartbook_set.all():
                    result += item.total_purchase_price
          return result
     
     @property
     def subtotal(self):
          result = 0
          if len(self.cartbook_set.all()) != 0:
               for item in self.cartbook_set.all():
                    result += item.subtotal_price
          return result
     
     @property
     def total(self):
          result = 0
          if len(self.cartbook_set.all()) != 0:
               for item in self.cartbook_set.all():
                    result += item.subtotal_price
          return (result - self.shipment_fee) or 0.00
     
    
     
class CartBook(models.Model):
     cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
     book = models.ForeignKey(Book, null=True, on_delete=models.SET_NULL)
     book_type_price = models.ForeignKey(BookTypePrice, null=True, blank=True, on_delete=models.CASCADE)
     book_quantity = models.IntegerField(default=0)
     book_price = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
     book_purchase_price = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
     
     def __str__(self):
          return str(self.cart.timestamp) or ""
     
     @property
     def total_purchase_price(self):
          if self.book_purchase_price is not None and self.book_purchase_price != 0 and self.book_quantity is not None and self.book_quantity != 0:
               return (self.book_quantity * self.book_purchase_price) or 0
          return 0
     
     
     # @property
     # def total_price(self):
     #      if (self.book_quantity is not None and self.book_quantity != 0 and 
     #          self.book_price is not None and self.book_price != 0 and self.book_discount is not None):
     #           return ((self.book_quantity * self.book_price) - (self.book_quantity * self.book_discount)) or 0
     #      return 0
     
     @property
     def subtotal_price(self):
          if (
               self.book_quantity is not None and self.book_quantity != 0 
               and self.book_price is not None and self.book_price != 0):
               return (self.book_quantity * self.book_price) or 0
          return 0
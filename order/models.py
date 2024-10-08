from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
import datetime
from django.db.models import Count, Sum, Avg

from azad.utils import unique_order_id_generator
from django.db.models.signals import pre_save, post_save

from billing.models import BillingProfile
from cart.models import Cart
from customer.models import Address


class ShipmentMethod(models.Model):
     region = models.CharField(max_length=255)
     shipment_comment = models.CharField(max_length=255, null=True, blank=True)
     shipment_fee = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
     free_shipment_limit = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
     active = models.BooleanField(default=True)
     
     def __str__(self):
          return self.region or ""
     
     # def get_absolute_url(self):
     #      return reverse('order:admin_shipment_detail', kwargs={'pk': self.pk})

class OrderManagerQuerySet(models.query.QuerySet):
     def recent(self):
          return self.order_by("-updated", "-timestamp")

     def get_sales_breakdown(self):
          recent = self.recent().not_refunded()
          recent_data = recent.totals_data()
          recent_cart_data = recent.cart_data()
          shipped = recent.not_refunded().by_status(status='shipped')
          shipped_data = shipped.totals_data()
          paid = recent.by_status(status='paid')
          paid_data = paid.totals_data()
          data = {
               'recent': recent,
               'recent_data':recent_data,
               'recent_cart_data': recent_cart_data,
               'shipped': shipped,
               'shipped_data': shipped_data,
               'paid': paid,
               'paid_data': paid_data
          }
          return data

     def by_weeks_range(self, weeks_ago=7, number_of_weeks=2):
          if number_of_weeks > weeks_ago:
               number_of_weeks = weeks_ago
          days_ago_start = weeks_ago * 7  # days_ago_start = 49
          days_ago_end = days_ago_start - (number_of_weeks * 7) #days_ago_end = 49 - 14 = 35
          start_date = timezone.now() - datetime.timedelta(days=days_ago_start)
          end_date = timezone.now() - datetime.timedelta(days=days_ago_end) 
          return self.by_range(start_date, end_date=end_date)

     def by_range(self, start_date, end_date=None):
          if end_date is None:
               return self.filter(updated__gte=start_date)
          return self.filter(updated__gte=start_date).filter(updated__lte=end_date)

     def by_date(self):
          now = timezone.now() - datetime.timedelta(days=9)
          return self.filter(updated__day__gte=now.day)

     def totals_data(self):
          return self.aggregate(Sum("total"), Avg("total"))

     def cart_data(self):
          return self.aggregate(
                         Sum("cart__products__price"), 
                         Avg("cart__products__price"), 
                         Count("cart__products")
                                        )

     def by_status(self, status="shipped"):
          return self.filter(status=status)

     def not_refunded(self):
          return self.exclude(status='refunded')

     def by_request(self, request):
          billing_profile, created = BillingProfile.objects.new_or_get(request)
          return self.filter(billing_profile=billing_profile)

     def not_created(self):
          return self.exclude(status='created')

class OrderManager(models.Manager):
     def get_queryset(self):
          return OrderManagerQuerySet(self.model, using=self._db)

     def by_request(self, request):
          return self.get_queryset().by_request(request)

     def new_or_get(self, billing_profile, cart_obj):
          created = False
          qs = self.get_queryset().filter(
                    billing_profile=billing_profile, 
                    cart=cart_obj, 
                    active=True, 
                    status='created'
               )
          if qs.count() == 1:
               obj = qs.first()
          else:
               obj = self.model.objects.create(
                         billing_profile=billing_profile, 
                         cart=cart_obj)
               created = True
          return obj, created



# Random, Unique
class Order(models.Model):
     class OrderStatus(models.TextChoices):
          Created = 'Created'
          Paid = 'Paid'
          Shipped = 'Shipped'
          Refunded = 'Refunded'
     billing_profile     = models.ForeignKey(BillingProfile, null=True, blank=True, on_delete=models.SET_NULL)
     order_id            = models.CharField(max_length=120, blank=True) # AB31DE3
     shipping_address    = models.ForeignKey(Address, related_name="shipping_address",null=True, blank=True, on_delete=models.SET_NULL)
     billing_address     = models.ForeignKey(Address, related_name="billing_address", null=True, blank=True, on_delete=models.SET_NULL)
     order_note          = models.TextField(blank=True, null=True)
     cart                = models.ForeignKey(Cart, on_delete=models.CASCADE)
     status              = models.CharField(max_length=120, choices=OrderStatus.choices, default=OrderStatus.Created)
     active              = models.BooleanField(default=True)
     updated             = models.DateTimeField(auto_now=True)
     timestamp           = models.DateTimeField(auto_now_add=True)

     def __str__(self):
          return self.order_id

     objects = OrderManager()

     class Meta:
          ordering = ['-timestamp', '-updated']

     def get_absolute_url(self):
          return reverse("orders:detail", kwargs={'order_id': self.order_id})

     def get_status(self):
          if self.status == "refunded":
               return "Refunded order"
          elif self.status == "shipped":
               return "Shipped"
          return "Shipping Soon"
     
     

@receiver(pre_save, sender=Order)
def pre_save_create_order_id(sender, instance, *args, **kwargs):
     if not instance.order_id:
          instance.order_id = unique_order_id_generator(instance)


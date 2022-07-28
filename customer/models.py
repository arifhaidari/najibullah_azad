from django.db import models
from django.urls import reverse

class Customer(models.Model):
     name = models.CharField(max_length=255)
     email = models.CharField(max_length=255)
     phone  = models.CharField(max_length=80, null=True, blank=True)
     
     def __str__(self):
          return self.name  or f"customer_object_{self.pk}"


class Address(models.Model):
     class Types(models.TextChoices):
          Billing = 'Billing'
          Shipping = 'Shipping'
          Both = 'Both'
          
     billing_profile = models.ForeignKey('billing.BillingProfile', on_delete=models.CASCADE, null=True)
     full_name   = models.CharField(max_length=255, null=True, blank=True)
     country   = models.CharField(max_length=255, null=True, blank=True)
     city     = models.CharField(max_length=255, null=True, blank=True)
     district    = models.CharField(max_length=255, null=True, blank=True)
     street  = models.CharField(max_length=255, null=True, blank=True)
     zipcode  = models.CharField(max_length=120, null=True, blank=True)
     phone  = models.CharField(max_length=120, null=True, blank=True)
     email  = models.CharField(max_length=255, null=True, blank=True)
     apartment  = models.CharField(max_length=255, null=True, blank=True)
     address_type    = models.CharField(max_length=120, choices=Types.choices, default=Types.Both)

     def __str__(self):
          if self.city and self.country:
               return f"{self.city}, {self.country}, {self.street}"
          return "my_address"

     def get_absolute_url(self):
          return reverse("address-update", kwargs={"pk": self.pk})
from pyexpat import model
import random
import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from django.db import models
from django.db.models import Q
from django.db.models.fields.related import ManyToManyField
from django.db.models.signals import post_delete, pre_save, post_save
from django.urls import reverse
from book.validators import image_valid_size, image_valid_type
from django.dispatch import receiver

# from ecommerce.aws.download.utils import AWSDownload
# from ecommerce.aws.utils import ProtectedS3Storage
from azad.utils import unique_slug_generator

# def get_filename_ext(filepath):
#      base_name = os.path.basename(filepath)
#      name, ext = os.path.splitext(base_name)
#      return name, ext


# def upload_image_path(instance, filename):
     # print(instance)
     #print(filename)
     # new_filename = random.randint(1,3910209312)
     # name, ext = get_filename_ext(filename)
     # final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
     # return f"books/{new_filename}_{filename}"


class Genere(models.Model):
     name = models.CharField(max_length=255)
     active = models.BooleanField(default=True)
     
     def __str__(self):
          return self.name or ""

class BookType(models.Model):
     name = models.CharField(max_length=255)
     active = models.BooleanField(default=True)
     
     def __str__(self):
          return self.name or ""

class BookManager(models.Manager):
     # def all(self):
     #      return self.get_queryset().active()

     def get_by_id(self, id):
          qs = self.get_queryset().filter(id=id) # Product.objects == self.get_queryset()
          if qs.count() == 1:
               return qs.first()
          return None

class Book(models.Model):
     title           = models.CharField(max_length=255)
     author           = models.CharField(max_length=255, default='Najibullah Azad')
     isbn           = models.CharField(max_length=255)
     page           = models.IntegerField(null=True, blank=True)
     slug            = models.SlugField(blank=True, unique=True)
     description     = models.TextField()
     category        = models.ManyToManyField(Genere, blank=True)
     active          = models.BooleanField(default=True)
     release_date       = models.DateField()
     timestamp       = models.DateTimeField(auto_now_add=True)
     updated         = models.DateTimeField(auto_now=True)

     objects = BookManager()
     
     # def get_absolute_url_admin(self):
     #      return reverse("product:admin_product_detail", kwargs={"slug": self.slug})

     def __str__(self):
          return self.title or self.pk or ""

     def get_absolute_url(self):
          return reverse("book:detail", kwargs={"slug": self.slug})

class OtherLink(models.Model):
     book = models.ForeignKey(Book, on_delete=models.CASCADE)
     platform = models.CharField(max_length=255)
     link = models.CharField(max_length=500)
     
     def __str__(self):
          return f"{self.book.title}-{self.platform}" or "other_link"


class BookTypePrice(models.Model):
     book = models.ForeignKey(Book, null=True, on_delete=models.SET_NULL)
     book_type = models.ForeignKey(BookType, null=True, on_delete=models.SET_NULL)
     purchase_price  = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
     price           = models.DecimalField(decimal_places=2, max_digits=20)
     old_price       = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
     is_media = models.BooleanField(default=True)
     
     def __str__(self):
          return f"{self.book.title}-{self.price}" or "book_type_price"
     

class BookCovers(models.Model):
     book = models.ForeignKey(Book, on_delete=models.CASCADE)
     image = models.ImageField(
          upload_to='books/', null=True, blank=True, validators=[image_valid_size, image_valid_type]
          )
     
     def __str__(self):
          return self.book.title or self.pk or ""
     
     # def delete(self, *args, **kwargs):
     #      print('delte the image ------')
     #      self.image.delete()
     #      super().delete(*args, **kwargs)

@receiver(post_delete, sender=BookCovers)
def post_delete_image(sender, instance, *args, **kwargs):
     """ Clean Old Image file """
     try:
          print('it is dlete dude =====')
          instance.image.delete(save=False)
     except:
          pass
   
def book_pre_save_receiver(sender, instance, *args, **kwargs):
     if not instance.slug:
          instance.slug = unique_slug_generator(instance)

pre_save.connect(book_pre_save_receiver, sender=Book)










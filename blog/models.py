from pyexpat import model
from django.db import models


class Category(models.Model):
     class Meta:
          # verbose_name = ''
          verbose_name_plural = 'Categories'
     name = models.CharField(max_length=256)
     active = models.BooleanField(default=True)

     def __str__(self):
          return self.name or f"post_category_object_{self.pk}"


class Tag(models.Model):
     name = models.CharField(max_length=256)
     active = models.BooleanField(default=True)

     def __str__(self):
          return self.name or f"post_tag_object_{self.pk}"

class Post(models.Model):
     title = models.CharField(max_length=256)
     body = models.TextField()
     image = models.ImageField(upload_to='blog/')
     categories = models.ManyToManyField(Category, blank=True)
     tags = models.ManyToManyField(Tag, blank=True)
     view = models.IntegerField(default=0)
     read_time = models.DecimalField(decimal_places=1, max_digits=3, default=0.0)
     active = models.BooleanField(default=True)
     timestamp = models.DateTimeField(auto_now_add=True)
     updated_at = models.DateTimeField(auto_now=True)

     def __str__(self):
          return self.title or f"post_object_{self.pk}"



from django.contrib import admin

from .models import Category, Tag, Post

admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(Post)
# admin.site.register(Post)
# now i want check if could whether i can update the online repository or not.

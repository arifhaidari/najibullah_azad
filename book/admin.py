from django.contrib import admin

from .models import Genere, Book, OtherLink, BookTypePrice, BookCovers, BookType

admin.site.register(Genere)
admin.site.register(Book)
admin.site.register(OtherLink)
admin.site.register(BookCovers)
admin.site.register(BookTypePrice)
admin.site.register(BookType)


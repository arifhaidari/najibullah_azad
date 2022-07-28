from django.shortcuts import render

from django.views.generic import View, DetailView

from book.models import Book


class Books(View):
     template_name = 'book/book_list.html'
     
     def get(self, request, *args, **kwargs):
          books = Book.objects.all()
          return render(request, self.template_name, {'books': books})


class BookDetail(DetailView):
     template_name = 'book/book_detail.html'
     model = Book
     
     def get_context_data(self, **kwargs):
          context = super().get_context_data(**kwargs)
          book_object = kwargs['object']
          try:
               context['other_books'] = Book.objects.exclude(id=book_object.id)
          except:
               context['other_books'] = None
          return context
          



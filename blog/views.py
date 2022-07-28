from django.shortcuts import render
from django.views.generic import View, DetailView

# Create your views here.

class AllPost(View):
     template_name = 'blog/all_post.html'
     
     def get(self, request, *args, **kwargs):
          return render(request, self.template_name, {})


class Archive(View):
     template_name = 'blog/archive.html'
     
     def get(self, request, *args, **kwargs):
          return render(request, self.template_name, {})  

class Tags(View):
     template_name = 'blog/tags.html'
     
     def get(self, request, *args, **kwargs):
          return render(request, self.template_name, {})


class Categories(View):
     template_name = 'blog/categories.html'
     
     def get(self, request, *args, **kwargs):
          return render(request, self.template_name, {})


class BlogDetail(View):
     template_name = 'blog/blog_detail.html'
     
     def get(self, request, *args, **kwargs):
          return render(request, self.template_name, {})

class SingleCategory(View):
     template_name = 'blog/single_category.html'
     
     def get(self, request, *args, **kwargs):
          return render(request, self.template_name, {})


class SingleTag(View):
     template_name = 'blog/single_tag.html'
     
     def get(self, request, *args, **kwargs):
          return render(request, self.template_name, {})
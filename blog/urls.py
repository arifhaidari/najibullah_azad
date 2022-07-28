from django.urls import path
from .views import AllPost, Tags, Categories, BlogDetail, SingleCategory, SingleTag, Archive

app_name = 'blog'

urlpatterns = [
     path('', AllPost.as_view(), name='all_post'),
     path('detail/', BlogDetail.as_view(), name='blog_detail'),
     path('archive/', Archive.as_view(), name='archive'),
     path('tag/', Tags.as_view(), name='tags'),
     path('category/', Categories.as_view(), name='categories'),
     path('category/single/', SingleCategory.as_view(), name='single_category'),
     path('tag/single/', SingleTag.as_view(), name='single_tag'),
]


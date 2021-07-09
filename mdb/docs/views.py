from django.shortcuts import render
from .models import *

def docs(request):
  categories = DocsPage.objects.filter(type = 'category').order_by('order')
  sub_categories = DocsPage.objects.filter(type = 'sub-category').order_by('order')
  # ~ print(f'c{categories}')
  #filter(type = 'category')\
  #  .values(['short_title', 'slug', 'type'])
  # ~ SubcategoryPages = DocsPage.objects.filter(type = 'sub-category')
  
  return render(request, 'docs/docs.html',
    {
      'categories': categories,
      'sub_categories': sub_categories
    }
  )

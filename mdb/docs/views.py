from django.shortcuts import render
from .models import *

def docs(request):
  categories = DocsPage.objects.filter(type = 'category').order_by('order')
  sub_categories = DocsPage.objects.filter(type = 'sub-category').order_by('order')
  
  return render(request, 'docs/docs.html',
    {
      'categories': categories,
      'sub_categories': sub_categories
    }
  )

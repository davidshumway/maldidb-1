from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django import forms

from .forms import *
from .models import *
from .tables import *
from .serializers import *

from spectra_search.views import SpectraFilter

import django_filters
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import SingleTableView
import django_tables2 as tables

from rest_framework.viewsets import ModelViewSet

class CollapsedCosineScoreViewSet(ModelViewSet):
  '''
  Showing latest three entries.
  '''
  serializer_class = CollapsedCosineScoreSerializer
  queryset = CollapsedCosineScore.objects.all().order_by('-id')[:3]
  
  def post():
    pass
    
class SpectraViewSet(ModelViewSet):
  '''
  Showing latest three entries.
  '''
  serializer_class = SpectraSerializer
  queryset = Spectra.objects.all().order_by('-id')[:3]
  
  def post():
    pass
    
class CollapsedSpectraViewSet(ModelViewSet):
  '''
  Showing latest three entries.
  '''
  serializer_class = CollapsedSpectraSerializer
  queryset = CollapsedSpectra.objects.order_by('-id')[:3]
  
  def post():
    pass
    
def spectra_profile(request, spectra_id):
  spectra = Spectra.objects.get(id = spectra_id)
  return render(request, 'spectra/spectra_profile.html', {'spectra': spectra})
  
@login_required
def edit_spectra(request, spectra_id):
  ''' edit details of spectra '''    
  if request.method == "POST":
    # instance kwargs passed in sets the user on the modelForm
    form = SpectraEditForm(request.POST, request.FILES,
      instance = Spectra.objects.get(id = spectra_id))
    if form.is_valid():
      form.save()
      return redirect(reverse('spectra:view_spectra', args = (lib_id, )))
  else:
    form = SpectraEditForm(instance = Spectra.objects.get(id = spectra_id))
  return render(request, 'spectra/edit_spectra.html', {'form': form})

@login_required
def add_post(request):
  if request.method == 'POST':
    form = SpectraForm(request.POST, request.FILES)
    if form.is_valid():
      post = form.save(commit = False)
      post.user = request.user
      post.created_by_id = request.user.id
      post.save()
      return redirect('chat:home')
  else:
    form = SpectraForm()
  return render(request, 'spectra/add_post.html', {'form': form})
      
class SpectraListView(SingleTableView):
  model = Spectra
  table_class = SpectraTable
  template_name = 'spectra/spectra.html'
  
  def get_queryset(self, *args, **kwargs):
    return Spectra.objects.filter(created_by = self.request.user) \
      .order_by('-id')

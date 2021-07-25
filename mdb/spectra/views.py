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

from chat.models import LabGroup, Library
from django.db.models import Q

from .wsviews import _cosine_score_libraries

class CollapsedCosineScoreViewSet(ModelViewSet):
  '''
  Showing latest ten entries.
  '''
  serializer_class = CollapsedCosineScoreSerializer
  queryset = CollapsedCosineScore.objects.all().order_by('-id')[:10]
  
  def post():
    pass
    
class SpectraViewSet(ModelViewSet):
  '''
  Showing latest ten entries.
  '''
  serializer_class = SpectraSerializer
  queryset = Spectra.objects.all().order_by('-id')[:10]
  
  def post():
    pass
    
class CollapsedSpectraViewSet(ModelViewSet):
  '''
  Showing latest ten entries.
  '''
  serializer_class = CollapsedSpectraSerializer
  queryset = CollapsedSpectra.objects.order_by('-id')[:10]
  
  def post():
    pass
    
def spectra_profile(request, spectra_id):
  spectra = Spectra.objects.get(id = spectra_id)
  return render(request, 'spectra/spectra_profile.html', {'spectra': spectra})

def spectra2_profile(request, spectra_id):
  spectra = CollapsedSpectra.objects.get(id = spectra_id)
  return render(request, 'spectra/spectra_profile.html', {'spectra': spectra})

# ~ @login_required
def lib_compare(request):
  if request.method == "POST":
    form = LibCompareForm(request.POST, request.FILES)
    if form.is_valid():
      #form.save()
      #return redirect(reverse('chat:view_metadata', args = (strain_id, )))
      pass
  else:
    form = LibCompareForm()
  # shows all available to user
  if request.user.is_authenticated:
    u = request.user
    user_labs = LabGroup.objects.filter(
      Q(owners__in = [u]) | Q(members__in = [u])
    )
    form.fields['library'].queryset = Library.objects.filter(
      Q(created_by__exact = u) | 
      Q(lab__in = user_labs) |
      Q(privacy_level__exact = 'PB')
    )
  else:
    form.fields['library'].queryset = Library.objects.filter(
      Q(privacy_level__exact = 'PB')
    )
  # ~ print(f'lib-compare form {form}')
  return render(request, 'spectra/lib_compare.html', {'form': form})
  
def lib_compare2(request, library_ids):
  '''
  Returns json response of library comparison
  '''
  # all available to user
  if request.user.is_authenticated:
    u = request.user
    user_labs = LabGroup.objects.filter(
      Q(owners__in = [u]) | Q(members__in = [u])
    )
    qs = Library.objects.filter(
      Q(created_by__exact = u) | 
      Q(lab__in = user_labs) |
      Q(privacy_level__exact = 'PB')
    ).filter(id__in = [ int(i) for i in library_ids.split(',')])
  else:
    qs = Library.objects.filter(
      Q(privacy_level__exact = 'PB')
    ).filter(id__in = [ int(i) for i in library_ids.split(',')])
  
  r = _cosine_score_libraries(list(qs.values_list('id', flat = True)))
  print(f'r{r}')
  
  # ~ print(f'form.is_valid()2{form.is_valid()}')
  # ~ ws = websocket.WebSocket()
  # ~ ws.connect('ws://localhost:8000/ws/pollData')
  # ~ ws.send(json.dumps({
    # ~ 'type': 'library comparison',
    # ~ 'data': {
      # ~ 'client': client,
      # ~ 'result': lib_score_parseresult(q[0].result)
    # ~ }
  # ~ }))
  # ~ ws.close()
  
  # ~ socket.send(JSON.stringify({
    # ~ type: 'library comparison',
    # ~ libraries: selected,
  # ~ }));
  
  # "TypeError: In order to allow non-dict objects to be serialized set
  # the safe parameter to False."
  return JsonResponse(r, safe = False)
  # ~ return render(request, 'spectra/lib_compare.html', {'form': form})
  
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

from django.shortcuts import render
from mdb.utils import *
from chat.models import *
from spectra.models import *
from accounts.models import *
from .forms import *
from .tables import *
from .serializers import *
from django.http import JsonResponse
import django_filters
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import SingleTableView
import django_tables2 as tables
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
# R
from chat.rfn import SpectraScores
# Distance measurement
#from sklearn.metrics.pairwise import cosine_similarity
# spectra table
from spectra.tables import *
# importer
from importer.views import idbac_sqlite_insert
# preprocess
import requests
import os
import shutil
import websocket
import operator
import json

# ~ from rest_framework.viewsets import ModelViewSet
# ~ class CollapsedCosineScoreViewSet(ModelViewSet):
  # ~ '''
  # ~ Showing latest three entries.
  # ~ '''
  # ~ serializer_class = CollapsedCosineScoreSerializer
  # ~ queryset = CollapsedCosineScore.objects.all()[:3]
  # ~ def post():
    # ~ pass
    
#-----------------------------------------------------------------------
# begin autocomplete views
#-----------------------------------------------------------------------
from dal import autocomplete
class MetadataAutocomplete(autocomplete.Select2QuerySetView):
  '''cKingdom = models.CharField(max_length = 255, blank = True)
  cPhylum = models.CharField(max_length = 255, blank = True)
  cClass = models.CharField(max_length = 255, blank = True)
  cOrder = models.CharField(max_length = 255, blank = True)
  cGenus = models.CharField(max_length = 255, blank = True)
  cSpecies
  
  https://github.com/yourlabs/django-autocomplete-light/issues/1072
  
  -- get_result_label, get_result_value, get_selected_result_label
     all take in an item (<Metadata object>) and return a string
     or by default <Metadata object>'s __str__ representation.
  '''
  view = None
  
  def __init__(self, *args, **kwargs):
    self.view = kwargs.get('view', None)
    
  def get_result_label(self, item):
    return getattr(item, self.view)

  def get_result_value(self, item):
    return getattr(item, self.view)
    # ~ return item.strain_id

  def get_selected_result_label(self, item):
    return getattr(item, self.view)
  
  def get_queryset(self):
    '''
    -- self.view is in [cKingdom, cPhylum, ...]
    -- Ignore empty forwards. But if a previous forward is filled, then
       clear the following forwards. That is, a change in upper level
       resets lower levels.
    '''
    try:
      print(f'fwd:{self.forwarded}')
    except:
      pass
    qs = Metadata.objects.all().order_by(self.view).distinct(self.view)
    if self.forwarded:
      for attr, val in self.forwarded.items():
        # ~ print(attr, val) # cKingdom ['Bacteria']
        if val == []: continue
        kwargs = {
          '{0}__{1}'.format(attr, 'in'): val # or qs.filter(abc=abc) ?
        }
        qs = qs.filter(**kwargs)
    
    if self.q:
      kwargs = {
        '{0}__{1}'.format(self.view, 'icontains'): self.q
        # ~ , '{0}__{1}'.format('name', 'endswith'): 'Z'
      }
      qs = qs.filter(**kwargs).order_by(self.view).distinct(self.view)
    return qs
#-----------------------------------------------------------------------
# end autocomplete views
#-----------------------------------------------------------------------

@start_new_thread
def process_file(request, file, form, owner, upload_count, client):
  '''
  Runs R methods to process a mzml or mzxml file
  '''
  try:
    ws = websocket.WebSocket()
    ws.connect('ws://localhost:8000/ws/pollData')
    
    # ~ print(f'preprocess file{file}')
    f1 = file.replace('uploads/', 'uploads/sync/')
    current_loc = '/home/app/web/media/' + file
    new_loc = '/' + file.replace('uploads/', 'uploads/sync/')
    os.system('cp ' + current_loc + ' ' + new_loc)
    data = {'file': f1}
    # ~ print(f'send{data}')
    r = requests.get('http://plumber:8000/preprocess', params = data)
    
    if r.text == '':
      # ex: "simpleWarning in if (class(input) == \"list\") {: the condition
      # has length > 1 and only the first element will be used\n"
      ws.send(json.dumps({
        'type': 'completed preprocessing',
        'data': {
          'count': upload_count,
          'client': client,
        }
      }))    
      ws.close()
      return
    # ~ t = UserTask.objects.create( # ok
      # ~ owner = request.user,
      # ~ task_description = 'idbac_sql'
    # ~ )
    # Adds sqlite spectra to db
    info = idbac_sqlite_insert(request, form,
      '/uploads/sync/' + str(r.json()[0]) + '.sqlite',
      user_task = False,
      upload_count = upload_count
    )
  except Exception as e:
    print('pf2', e)
  
  # Communicates completion back to upload
  try:
    ws.send(json.dumps({
      'type': 'completed preprocessing',
      'data': {
        'count': upload_count,
        'client': client,
      }
    }))    
    ws.close()
  except:
    print('pf1')
    try:
      ws = websocket.WebSocket()
      ws.connect('ws://localhost:8000/ws/pollData')
      ws.send(json.dumps({
        'type': 'completed preprocessing',
        'data': {
          'count': upload_count,
          'client': client,
        }
      }))    
      ws.close()
    except:
      print('pf3')
  return
  
def upload_status(request):
	pass 

@login_required
def ajax_upload_library(request):
  '''
  Validates form before upload
  '''
  if request.method == 'POST':
    form = SpectraLibraryForm(data = request.POST, files = request.FILES,
      request = request)
    if form.is_valid():
      if form.cleaned_data['search_library']:
        return JsonResponse({ # search
            'status': 'success', 
            'data': {
              'library': form.cleaned_data['library'].title,
              'library_id': form.cleaned_data['library'].id,
              'search_library': form.cleaned_data['search_library'].id
            }
          }, 
          status=200)
      else:
        return JsonResponse({ # upload only
            'status': 'success', 
            'data': {
              'library': form.cleaned_data['library'].title,
              'library_id': form.cleaned_data['library'].id,
              'search_library': False
            }
          }, 
          status=200)
    else:
      e = form.errors.as_json()
      return JsonResponse({'errors': e}, status=400)
  else:
    return JsonResponse({'errors': 'Empty request.'}, status=400)

@login_required
def ajax_upload(request):
  '''
  Uploads one or more files.
  
  Preprocessing (optional) - Once uploaded, spawn new thread to preprocess.
  UserFile has file location, e.g., "uploads/Bacillus_ByZQI1O.mzXML".
  If owner=None, then CollapsedSpectra.create(created_by=None) still works.
  Todo: Anonymous session to access anon. upload.
  '''
  if request.method == 'POST':
    form = SpectraUploadForm(data = request.POST, files = request.FILES,
      request = request
    )
    if form.is_valid():
      form.request = request # pass request to save() method
      form.save() # Django saves the file
      owner = request.user.id #if request.user.is_authenticated else None
      # ~ lab, created = LabGroup.objects.get_or_create(
        # ~ lab_name = 'FileUploads' # initializes file uploads group
      # ~ )
      # ~ form.cleaned_data['lab'] = lab
      form.cleaned_data['library'] = Library.objects.get(
        id = form.cleaned_data['library_id'])
        
      file = str(form.instance.file)
      
      form.cleaned_data['privacy_level'] = ['PR']
      process_file(request, file, form, owner,
        form.cleaned_data['upload_count'], form.cleaned_data['client'])
      return JsonResponse({'status': 'preprocessing'}, status=200)
    else:
      e = form.errors.as_json()
      return JsonResponse({'errors': e}, status=400)
        
    
    # ~ if form.is_valid():
      # ~ form.request = request # pass request to save() method
      # ~ form.save()
      
      #print(f'form.cleaned_data {form.cleaned_data}')
      # ~ return JsonResponse({'status': form.cleaned_data}, status=200)
      
      # ~ count = 0
      # ~ for field in request.FILES.keys():
        # ~ for file in request.FILES.getlist(field):
          #save_uploaded_file_to_media_root(formfile)
          
      # ~ return JsonResponse(
        # ~ {'status': 'preprocessing'},
        # ~ {'status': 'preprocessing', 'task': t.id},
        # ~ status=200)
      # ~ return JsonResponse({'status': 'ready'}, status=200)
    # ~ else:
      # ~ print('invalid form')
      # ~ e = form.errors.as_json()
      # ~ return JsonResponse({'errors': e}, status=400)
  return JsonResponse({'errors': 'Empty request.'}, status=400)
  
class SpectraFilter(django_filters.FilterSet):
  library = django_filters.ModelMultipleChoiceFilter(
    queryset = Library.objects.all()
  )
  description = django_filters.CharFilter(lookup_expr = 'icontains')

  class Meta:
    model = Spectra
    exclude = ('id', 'picture')
  
class CollapsedSpectraFilter(django_filters.FilterSet):
  library = django_filters.ModelMultipleChoiceFilter(
    queryset = Library.objects.all()
  )
  description = django_filters.CharFilter(lookup_expr = 'icontains')

  class Meta:
    model = CollapsedSpectra
    exclude = ('id', 'picture')

class FilteredSpectraListView(SingleTableMixin, FilterView):
  table_class = SpectraTable
  model = Spectra
  template_name = 'spectra_search/search_results.html'
  filterset_class = SpectraFilter
  
  def get_queryset(self):
    pass

class FilteredCollapsedSpectraListView(SingleTableMixin, FilterView):
  table_class = CollapsedSpectraTable
  model = CollapsedSpectra
  template_name = 'spectra_search/search_results.html'
  filterset_class = CollapsedSpectraFilter
  
  def get_queryset(self):
    # self.queryset
    #pass
    #self.queryset
    from django.db.models import Count
    qs = super().get_queryset()
    qs = qs.annotate(num_spectra = Count('collapsed_spectra'))
    return qs

@method_decorator(login_required, name = 'dispatch')
class FilteredSpectraSearchListView(SingleTableMixin, FilterView):
  '''
  todo: combine filter.form and table
  table: CosineSearchTable
  filter: SpectraFilter
  form: SpectraSearchForm
  '''
  table_class = CosineSearchTable
  model = Spectra
  template_name = 'spectra_search/basic_search.html'
  filterset_class = SpectraFilter
  # ~ show_tbl = False
  
  def get_context_data(self, **kwargs):
    '''Render filter widget to pass to the table template.
    '''
    context = super().get_context_data(**kwargs)
    
    # metadata form
    context['metadata_form'] = SpectraCollectionsForm()
    
    # search library form
    # ~ context['spectra_search_type_form'] = SpectraSearchTypeForm(request = self.request)
    
    # upload form
    context['upload_form'] = SpectraLibraryForm(request = self.request)
    u = self.request.user
    
    # all (using bitwise or https://github.com/django/django/blob/
    #   master/django/db/models/query.py#L308)
    all = Library.objects.none()
    # r01
    alice, created = User.objects.get_or_create(username = 'alice')
    q = Library.objects.filter(title__exact = 'R01 Data',
      created_by__exact = alice)
    all = all | q
    context['upload_form'].fields['search_library'].queryset = q
    # own libraries (library_select shares this qs)
    q = Library.objects.filter(created_by__exact = u)
    all = all | q
    context['upload_form'].fields['search_library_own'].queryset = q
    context['upload_form'].fields['library_select'].queryset = q
    # own labs
    user_labs = LabGroup.objects.filter(
      Q(owners__in = [u]) | Q(members__in = [u])
    )
    q = Library.objects.filter(
      Q(lab__in = user_labs)
    ).order_by('-id')
    all = all | q
    context['upload_form'].fields['search_library_lab'].queryset = q
    # public
    q = Library.objects.filter(privacy_level__exact = 'PB').order_by('-id')
    context['upload_form'].fields['search_library_public'].queryset = q
    all = all | q
    # all libraries
    context['upload_form'].fields['search_from_existing'].queryset = all
    
    f = SpectraFilter(self.request.GET, queryset = self.queryset)
    context['filter'] = f
    
    for attr, field in f.form.fields.items():
      context['table'].columns[attr].w = field.widget.render(attr, '')
    
    # addl options
    main_fields = [
      'spectra_file','replicates','spectrum_cutoff','spectrum_cutoff_low',
      'spectrum_cutoff_high','preprocessing','peak_mass','peak_intensity',
      'peak_snr',
    ]
    # secondary but display on top
    secondary_top = [
      'lab_nameXX', 'libraryXX', 'strain_idXX', 'created_byXX',
      'xml_hashXX',
    ]
    # secondary other
    secondary_form = []
    
    context['table'].sfilter = f
    context['table'].table_type = 'spectra'
    
    if self.request.GET.get('peak_mass'):
      form = SpectraSearchForm(self.request.GET, self.request.FILES,
        initial = {'spectrum_cutoff': 'protein', 'replicates': 'collapsed'}
      )
    else:
      form = SpectraSearchForm()
    
    # ~ if self.show_tbl is True:
      # ~ form.show_tbl = True
    # ~ else:
      # ~ form.show_tbl = False
    
    # Addl fields
    for tag, field in form.fields.items():
      if tag not in main_fields:
        if tag not in secondary_top: #forms.forms. in django 2.2
          boundField = forms.BoundField(form, form.fields[tag], tag)
          secondary_form.append(boundField)
        else: # Prepend, add to index = 0
          boundField = forms.BoundField(form, form.fields[tag], tag)
          boundField.label = boundField.label.replace('xx', '')
          secondary_form.insert(0, boundField)
    
    context['form'] = form
    context['secondary_form_fields'] = secondary_form
    
    return context
  
  def get_queryset(self, *args, **kwargs):
    '''
    -- Calling queryset.update does not update the model.
    -- Use min_mass and max_mass, not tof_mode, to differentiate sm and
       proteins
    -- With user's spectra and db spectra in place, the search should
       be cached after first processing takes place, 
       as long as db rows did not change in the meantime.
    '''
    if len(self.request.GET) == 0:
      return Spectra.objects.none()

def sort_func(e):
  return e['score']

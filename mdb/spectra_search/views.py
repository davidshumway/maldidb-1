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
def process_file(request, file, form, owner, upload_count, ip):
  '''Runs R methods to process a spectra file
  
  Todo: Include user feedback
  '''
  ws = websocket.WebSocket()
  ws.connect('ws://localhost:8000/ws/pollData')
  # ~ ws.connect('ws://' + ip)
  # ~ ws.send('{"message": ""}')
  
  print(f'preprocess file{file}')
  f1 = file.replace('uploads/', 'uploads/sync/')
  current_loc = '/home/app/web/media/' + file
  new_loc = '/' + file.replace('uploads/', 'uploads/sync/')
  os.system('cp ' + current_loc + ' ' + new_loc)
  data = {'file': f1}
  print(f'send{data}')
  r = requests.get('http://plumber:8000/preprocess', params = data)

  # Adds sqlite spectra to db
  info = idbac_sqlite_insert(request, form,
    '/uploads/sync/' + str(r.json()[0]) + '.sqlite',
    user_task = False
  )
  
  # Communicates completion back to upload
  ws.send(json.dumps({
    'type': 'completed preprocessing',
    'data': {
      'count': upload_count,
      'client': ip,
    }
  }))
  
  ws.close()
  return


  
  # Collapse if there is a protein spectra
  if info['spectra']['protein'] > 0: ##### > 1
    data = {
      'id': form.cleaned_data['library'].id,
      'owner': owner
    }
    r = requests.get(
      'http://plumber:8000/collapseLibrary',
      params = data
    )
    
  # In the case of a collapsed spectra which had mass > 6000 but
  # when collapsed lost those peaks, it is necessary to 
  # retrieve the CollapsedSpectra using the spectra_content
  # attribute.
  n1 = CollapsedSpectra.objects.filter( # unknown spectra
    library_id__exact = form.cleaned_data['library'].id,
    spectra_content__exact = 'PR'
  ).first()
  n2 = CollapsedSpectra.objects.filter(
    library__exact = form.cleaned_data['search_library'].id,
    spectra_content__exact = 'PR'
  ).order_by('id').values('id')#, 'strain_id')
  data = {
    'ids': [n1.id] + [s['id'] for s in list(n2)]
  }
  r = requests.post(
    'http://plumber:8000/cosine',
    params = data
  )
  
  tmp = r.json()['binnedPeaks']
  binned_peaks = {}
  for v in tmp: # Dictionary of binned peaks
    binned_peaks[str(v['csId'][0])] = {
      'mass': v['mass'],
      'intensity': v['intensity'],
      'snr': v['snr'],
    }
  
# ~ # test
# ~ from spectra.models import *
# ~ import requests
# ~ n2 = CollapsedSpectra.objects.filter(
# ~ library__title__exact = 'R01 Data',
# ~ max_mass__gt = 6000
# ~ ).values('id')
# ~ data = {'ids': [2] + [s['id'] for s in list(n2)]}
# ~ r = requests.post('http://plumber:8000/cosine', params = data)
# ~ # create a dictionary and sort by its values
# ~ from collections import OrderedDict
# ~ k = [str(s['id']) for s in list(n2)] # one less
# ~ v = r.json()[1:] # one more, remove first
# ~ o = OrderedDict(
# ~ sorted(dict(zip(k, v)).items(),
  # ~ key = lambda x: (x[1], x[0]), reverse = True)
# ~ )

  # Dictionary sorted by its values
  from collections import OrderedDict
  k = [str(s['id']) for s in list(n2)] # one less
  v = r.json()['similarity'][1:] # one more remove first???
  o = OrderedDict(
    sorted(dict(zip(k, v)).items(),
      key = lambda x: (x[1], x[0]), reverse = True)
  )

  obj = CollapsedCosineScore.objects.create(
    spectra = n1,
    library = form.cleaned_data['library'], # lib unnecessary in ccs model
    scores = ','.join(map(str, list(o.values()))),
    spectra_ids = ','.join(map(str, o.keys())))
  
  if obj:
    l = {
      'result': [],
      'original': {
        'peak_mass': n1.peak_mass,
        'peak_intensity': n1.peak_intensity,
        'binned_mass': binned_peaks[str(n1.id)]['mass'],
        'binned_intensity': binned_peaks[str(n1.id)]['intensity'],
        'binned_snr': binned_peaks[str(n1.id)]['snr'],
      }
    }
    
    from django.db.models import Case, When
    preserved = Case(*[When(pk = pk, then = pos) for pos, pk in enumerate(o)])
    q = CollapsedSpectra.objects.filter(id__in = o.keys()).order_by(preserved)
    rowcount = 1
    for cs in q:
      l['result'].append({
        'score': o[str(cs.id)],
        'strain': cs.strain_id.strain_id,
        'kingdom': cs.strain_id.cKingdom,
        'phylum': cs.strain_id.cPhylum,
        'class': cs.strain_id.cClass,
        'order': cs.strain_id.cOrder,
        # ~ 'family': cs.strain_id.cFamily,
        'genus': cs.strain_id.cGenus,
        'species': cs.strain_id.cSpecies,
        'rowcount': rowcount,
        'peak_mass': cs.peak_mass,
        'peak_intensity': cs.peak_intensity,
        'binned_mass': binned_peaks[str(cs.id)]['mass'],
        'binned_intensity': binned_peaks[str(cs.id)]['intensity'],
        'binned_snr': binned_peaks[str(cs.id)]['snr'],
      })
      rowcount += 1
    ws.send(json.dumps(l))
  # ~ else:
    # ~ pass
    # ~ r = requests.post(
      # ~ 'http://plumber:8000/cosine',
      # ~ params = data
    # ~ )
  #scoring
  
def upload_status(request):
	pass 
  
def ajax_upload_library(request):
  if request.method == 'POST':
    form = SpectraLibraryForm(data = request.POST, files = request.FILES,
      request = request)
    if form.is_valid():
      # ~ form.request = request # pass request to save() method
      # ~ form.save()
      return JsonResponse({
          'status': 'success', 
          'data': {
            'library': form.cleaned_data['library'].title,
            'search_library': form.cleaned_data['search_library'].id
          }
        }, 
        status=200)
    else:
      e = form.errors.as_json()
      return JsonResponse({'errors': e}, status=400)
  else:
    return JsonResponse({'errors': 'Empty request.'}, status=400)
    
def ajax_upload(request):
  '''
  Preprocessing (optional) - Once uploaded, spawn new thread to preprocess.
  
  UserFile has file location, e.g., "uploads/Bacillus_ByZQI1O.mzXML".
  
  If owner=None, then CollapsedSpectra.create(created_by=None) still works.
   
  Todo: Anonymous session to access anon. upload.
  '''
  print(f'request.POST{request.POST}')
  if request.method == 'POST':
    form = SpectraUploadForm(data = request.POST, files = request.FILES,
      request = request#,
      # ~ library = Library.objects.filter(title__exact = request.POST.get('library'),
        # ~ created_by__exact = request.user)
    )
    if form.is_valid():
      form.request = request # pass request to save() method
      form.save() # Django saves the file
      owner = request.user.id if request.user.is_authenticated else None
      lab, created = LabGroup.objects.get_or_create(
        lab_name = 'FileUploads' # initializes file uploads group
      )
      form.cleaned_data['lab'] = lab
      form.cleaned_data['library'] = Library.objects.filter(
        title__exact = request.POST.get('tmp_library'),
        created_by__exact = request.user).first()
        
      # ~ if form.cleaned_data['preprocess'] == True:
      file = str(form.instance.file)
      # ~ filename = file.replace('uploads/', '')
      form.cleaned_data['privacy_level'] = ['PR']
      process_file(request, file, form, owner,
        form.cleaned_data['upload_count'], form.cleaned_data['ip'])
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
    q = Library.objects.none()
    if u.is_authenticated is False:
      q = Library.objects.filter(privacy_level__exact = 'PB')
    else:
      # This filters for only libraries accessible to the user
      # based on user access controls
      # ~ user_labs = LabGroup.objects \
        # ~ .filter(Q(owners__in = [u]) | Q(members__in = [u]))
      # ~ q = Library.objects \
        # ~ .filter(~Q(lab__lab_name__exact = 'FileUploads')) \
        # ~ .filter(\
          # ~ Q(lab__in = user_labs) | Q(privacy_level__exact = 'PB') | \
          # ~ Q(created_by__exact = u)
        # ~ ).order_by('-id')
      alice, created = User.objects.get_or_create(username = 'alice')
      q = Library.objects.filter(title__exact = 'R01 Data',
        created_by__exact = alice)
    context['upload_form'].fields['search_library'].queryset = q
    
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
    
    # ~ form = SpectraSearchForm(self.request.GET, self.request.FILES)
    # ~ if form.is_valid():
      # ~ print('valid form')
      # ~ pass
    # ~ else:
      # ~ print('invalid form')
      # ~ return self.queryset
    
    # ~ sm = form.cleaned_data['peak_mass'];
    # ~ si = form.cleaned_data['peak_intensity'];
    # ~ sn = form.cleaned_data['peak_snr'];
    # ~ srep = form.cleaned_data['replicates'];
    # ~ scut = form.cleaned_data['spectrum_cutoff'];
    # ~ if sm and si and sn and srep and scut:
      # ~ self.show_tbl = True
      
      # ~ # Create a search object for user, or anonymous user
      # ~ try:
        # ~ obj, created = SearchSpectra.objects.get_or_create(
          # ~ peak_mass = sm,
          # ~ peak_intensity = si,
          # ~ peak_snr = sn,
          # ~ created_by = self.request.user)
      # ~ except:
        # ~ obj, created = SearchSpectra.objects.get_or_create(
          # ~ peak_mass = sm,
          # ~ peak_intensity = si,
          # ~ peak_snr = sn,
          # ~ created_by = None)
      
      # ~ search_id = obj.id
      
      # ~ if srep == 'collapsed':
        # ~ n = CollapsedSpectra.objects.all()
      # ~ else:
        # ~ n = Spectra.objects.all()
      
      # ~ # tof_mode
      # ~ if scut == 'small':
        # ~ n = n.filter(max_mass__lt = 6000)
      # ~ elif scut == 'protein': # protein
        # ~ n = n.filter(max_mass__gt = 6000)
      # ~ else: # protein
        # ~ pass
      
      # ~ # optionals
      # ~ slib = form.cleaned_data['libraryXX'];
      # ~ slab = form.cleaned_data['labXX'];
      # ~ ssid = form.cleaned_data['strain_idXX'];
      # ~ sxml = form.cleaned_data['xml_hashXX'];
      # ~ scrb = form.cleaned_data['created_byXX'];
      # ~ #print(f'fcd: {form.cleaned_data}' ) # 
      # ~ if slib.exists():
        # ~ n = n.filter(library__in = slib)
      # ~ if slab.exists():
        # ~ n = n.filter(lab_name__in = slab)
      # ~ if ssid.exists():
        # ~ n = n.filter(strain_id__in = ssid)
      # ~ if sxml.exists():
        # ~ n = n.filter(xml_hash__in = sxml)
      # ~ if scrb.exists():
        # ~ n = n.filter(created_by__in = scrb)
      # ~ n = n.order_by('xml_hash')
      
      # ~ idx = {}
      # ~ count = 0
      
      # ~ search_ids = []
      # ~ for spectra in n:
        # ~ search_ids.append(spectra.id)
        # ~ idx[count] = spectra
        # ~ count += 1
      
      # ~ # bin  
      # ~ #result = sc.bin_peaks()
      # ~ import requests
      # ~ headers = {'"Content-Type': 'application/json"'}
      # ~ payload = {'id': search_id, 'ids': search_ids}
      # ~ r = requests.post(
        # ~ 'http://plumber:7002/binPeaks',
        # ~ data = payload, headers = headers
      # ~ )
      # ~ result = r.json() # built-in requests method
      # ~ print('result is:', result)
      
      # ~ # sort by key
      # ~ from django.db.models import Case, When
      # ~ sorted_list = []
      # ~ pk_list = []
      # ~ scores = {}
      # ~ first = True
      # ~ for key, value in result.items():
        # ~ if first: # skip first
          # ~ first = False
          # ~ continue
        # ~ k = int(key) - 2 # starts with 1, and 1st is search spectra
        # ~ sorted_list.append({'id': idx[k].id, 'score': float(value)})
        # ~ scores[idx[k].id] = float(value)
      # ~ sorted_list.sort(key = sort_func, reverse = True)
      # ~ pk_list = [key.get('id') for key in sorted_list]
      # ~ preserved = Case(*[When(pk = pk, then = pos) for pos, pk in enumerate(pk_list)])
      # ~ q = Spectra.objects.filter(id__in = pk_list).order_by(preserved)
      
      # ~ # Overwrite table data to add custom data, i.e., the score
      # ~ self.table_data = {'scores': scores, 'queryset': q}
      
      # ~ # Returns a queryset
      # ~ return q

    # ~ # Empty queryset
    # ~ return Spectra.objects.none()

def sort_func(e):
  return e['score']

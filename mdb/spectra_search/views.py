from django.shortcuts import render
from mdb.utils import *
from chat.models import *
from spectra.models import *
from .forms import *
from django.http import JsonResponse
from .tables import *
import django_filters
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import SingleTableView
import django_tables2 as tables
# R
from chat.rfn import SpectraScores
# Distance measurement
from sklearn.metrics.pairwise import cosine_similarity
# spectra table
from spectra.tables import SpectraTable

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
      qs = qs.filter(**kwargs
      ).order_by(self.view).distinct(self.view)
    return qs
#-----------------------------------------------------------------------
# end autocomplete views
#-----------------------------------------------------------------------

@start_new_thread
def preprocess_file(file, user_task):
  '''Run R methods to preprocess spectra file
  -- add Spectra and update UserFile
  '''
  import os
  import shutil
  print(f'preprocess file{file}')
  print('??')
  f1 = file.replace('uploads/', 'uploads/sync/')
  
  current_loc = '/home/app/web/media/' + file
  new_loc = '/' + file.replace('uploads/', 'uploads/sync/')
  os.system('cp ' + current_loc + ' ' + new_loc)
  
  #shutil.copyfile(current_loc, new_loc)
  
  import requests
  data = {'file': f1}
  print(f'send{data}')
  r = requests.get('http://plumber:8000/preprocess', params = data)
  print(r)
  print(r.content)

def ajax_upload(request):
  '''
  -- Preprocessing (optional) - Once uploaded, spawn new thread to preprocess.
  -- UserFile has file location, e.g., "uploads/Bacillus_ByZQI1O.mzXML".
  -- Library (optional) - After optional preprocessing, add file
    to the user's requested library, or user's "uploaded" spectra
    if not selected, or "anonymous" spectra collection if uploaded by
    a guest user.
  -- What happens if file / mzml contains more than one spectra?
    Answer: Probably throw an error.
  '''
  if request.method == 'POST':
    form = SpectraUploadForm(data=request.POST, files=request.FILES)
    if form.is_valid():
      print('valid form')
      form.request = request # pass request to save() method
      form.save()
      if form.cleaned_data['preprocess'] == True:
        # optional new thread to preprocess
        t = UserTask.objects.create(
          owner = request.user,
          task_description = 'preprocess'
        )
        t.statuses.add(UserTaskStatus.objects.create(
          status = 'start', user_task = t))
        preprocess_file(str(form.instance.file), t)
        return JsonResponse({'status': 'preprocessing'}, status=200)
      # add to library..
      
      return JsonResponse({'status': 'ready'}, status=200)
    else:
      print('invalid form')
      e = form.errors.as_json()
      return JsonResponse({'errors': e}, status=400)
  return JsonResponse({'errors': 'Empty request.'}, status=400)
  
class SpectraFilter(django_filters.FilterSet):
  library = django_filters.ModelMultipleChoiceFilter(
    queryset = Library.objects.all()
  )
  description = django_filters.CharFilter(lookup_expr = 'icontains')

  class Meta:
    model = Spectra
    exclude = ('id','picture') #fields = ['name', 'price', 'manufacturer']

class FilteredSpectraListView(SingleTableMixin, FilterView):
  table_class = SpectraTable
  model = Spectra
  template_name = 'spectra_search/search_results.html'
  filterset_class = SpectraFilter
  
  def get_queryset(self):
    pass

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
  show_tbl = False
  
  def get_context_data(self, **kwargs):
    '''Render filter widget to pass to the table template.
    '''
    context = super().get_context_data(**kwargs)
    
    # metadata form
    context['metadata_form'] = SpectraCollectionsForm()
    
    # upload form
    context['upload_form'] = SpectraUploadForm()
    
    f = SpectraFilter(self.request.GET, queryset = self.queryset)
    context['filter'] = f
    
    for attr, field in f.form.fields.items():
      context['table'].columns[attr].w = field.widget.render(attr, '')
      # ~ for attr2, value2 in value.__dict__.items():
        # ~ widget = value2.widget
        # ~ context['table'].columns[widget.name] = widget.render()
    
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
    
    # ~ print(f'gg: {self.request.GET}' ) # 
    # ~ print(f'gg: {self.request.GET.get("peak_mass")}' ) # 
    if self.request.GET.get('peak_mass'):
      form = SpectraSearchForm(self.request.GET, self.request.FILES,
        initial = {'spectrum_cutoff': 'protein', 'replicates': 'collapsed'}
      )
    else:
      form = SpectraSearchForm()
    
    if self.show_tbl is True:
      form.show_tbl = True
    else:
      form.show_tbl = False
    
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
    # Basic: Make a new SearchSpectra and then compare to all Spectra
    
    if len(self.request.GET) == 0:
      return Spectra.objects.none()
    # ~ print(f'gq-args: {args}' ) # 
    # ~ print(f'gq-kw: {kwargs}' ) # 
    # ~ print(f'gq-sr: {self.request}' ) # 
    # ~ print(f'gq-get: {self.request.GET}' ) # 
    
    form = SpectraSearchForm(self.request.GET, self.request.FILES)
    if form.is_valid():
      print('valid form')
      pass
    else:
      print('invalid form')
      return self.queryset
    
    sm = form.cleaned_data['peak_mass'];
    si = form.cleaned_data['peak_intensity'];
    sn = form.cleaned_data['peak_snr'];
    srep = form.cleaned_data['replicates'];
    scut = form.cleaned_data['spectrum_cutoff'];
    if sm and si and sn and srep and scut:
      print('valid data')
      self.show_tbl = True
      
      # Create a search object for user, or anonymous user
      try:
        obj, created = SearchSpectra.objects.get_or_create(
          peak_mass = sm,
          peak_intensity = si,
          peak_snr = sn,
          created_by = self.request.user
        )
      except:
        obj, created = SearchSpectra.objects.get_or_create(
          peak_mass = sm,
          peak_intensity = si,
          peak_snr = sn,
          created_by = None
        )
      
      search_id = obj.id
      
      n = Spectra.objects.all()
      
      # tof_mode
      if scut == 'small':
        n = n.filter(max_mass__lt = 6000)
      elif scut == 'protein': # protein
        n = n.filter(max_mass__gt = 6000)
      else: # protein
        pass
      
      # optionals
      slib = form.cleaned_data['libraryXX'];
      slab = form.cleaned_data['lab_nameXX'];
      ssid = form.cleaned_data['strain_idXX'];
      sxml = form.cleaned_data['xml_hashXX'];
      scrb = form.cleaned_data['created_byXX'];
      #print(f'fcd: {form.cleaned_data}' ) # 
      if slib.exists():
        n = n.filter(library__in = slib)
      if slab.exists():
        n = n.filter(lab_name__in = slab)
      if ssid.exists():
        n = n.filter(strain_id__in = ssid)
      if sxml.exists():
        n = n.filter(xml_hash__in = sxml)
      if scrb.exists():
        n = n.filter(created_by__in = scrb)
      n = n.order_by('xml_hash')
      
      idx = {}
      count = 0
      
      search_ids = []
      for spectra in n:
        search_ids.append(spectra.id)
        idx[count] = spectra
        count += 1
      
      # bin  
      #result = sc.bin_peaks()
      import requests
      headers = {'"Content-Type': 'application/json"'}
      payload = {'id': search_id, 'ids': search_ids}
      r = requests.post(
        'http://plumber:7002/binPeaks',
        data = payload, headers = headers
      )
      result = r.json() # built-in requests method
      print('result is:', result)
      
      # sort by key
      from django.db.models import Case, When
      sorted_list = []
      pk_list = []
      scores = {}
      first = True
      for key, value in result.items():
        if first: # skip first
          first = False
          continue
        k = int(key) - 2 # starts with 1, and 1st is search spectra
        sorted_list.append({'id': idx[k].id, 'score': float(value)})
        scores[idx[k].id] = float(value)
      sorted_list.sort(key = sort_func, reverse = True)
      pk_list = [key.get('id') for key in sorted_list]
      preserved = Case(*[When(pk = pk, then = pos) for pos, pk in enumerate(pk_list)])
      q = Spectra.objects.filter(id__in = pk_list).order_by(preserved)
      
      # Overwrite table data to add custom data, i.e., the score
      self.table_data = {'scores': scores, 'queryset': q}
      
      # Returns a queryset
      return q

    # Empty queryset
    return Spectra.objects.none()

def sort_func(e):
  return e['score']

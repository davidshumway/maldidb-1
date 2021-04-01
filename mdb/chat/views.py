from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django import forms

from .forms import *
from .models import *

from django.db.models import Q
from django.views.generic import TemplateView, ListView

from .tables import LibraryTable, SpectraTable, MetadataTable, \
  LabgroupTable, CosineSearchTable, XmlTable, LibCollapseTable, \
  UserTaskTable
  #UserLogsTable

import django_filters
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import SingleTableView
import django_tables2 as tables

# Distance measurement
from sklearn.metrics.pairwise import cosine_similarity

# R
from .rfn import SpectraScores

from mdb.utils import *

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
  print(f'preprocess file{file}')
  f1 = file.replace('uploads/', 'uploads/sync/')
  # file
  #import os
  #os.chmod('/home/app/web/media/' + file, 0o777)
  import os
  import shutil
  shutil.copyfile('/home/app/web/media/' + file, '/' + f1)
  
  import requests
  data = {'file': f1}
  r = requests.get('http://plumber:8000/preprocess', params = data)
  # ~ pass
  # ~ result = R['preprocess'](file)
  # ~ #print(f'pp result{result}')
  # ~ if result.rx2('error'):
    # ~ user_task.statuses.add(
      # ~ UserTaskStatus.objects.create(
        # ~ status = 'error', extra = result.rx2('error'),
        # ~ user_task = user_task
    # ~ ))
    # ~ user_task.statuses.add(
      # ~ UserTaskStatus.objects.create(
        # ~ status = 'complete', user_task = user_task
    # ~ ))
  
  #if result

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
      # add to library
      
      return JsonResponse({'status': 'ready'}, status=200)
    else:
      print('invalid form')
      e = form.errors.as_json()
      return JsonResponse({'errors': e}, status=400)
  return JsonResponse({'errors': 'Empty request.'}, status=400)
  
def user_task_status_profile(request, status_id):
  uts = UserTaskStatus.objects.get(id = status_id)
  return render(
      request,
      'chat/user_task_status_profile.html',
      {'user_task_status': uts}
  )
  
def metadata_profile(request, strain_id):
  md = Metadata.objects.get(strain_id = strain_id)
  return render(
      request,
      'chat/metadata_profile.html',
      {'metadata': md}
  )

def xml_profile(request, xml_hash):
  xml = XML.objects.get(xml_hash = xml_hash)
  lab = LabGroup.objects.get(lab_name = xml.lab_name)
  return render(
      request,
      'chat/xml_profile.html',
      {'xml': xml, 'lab': lab}
  )

def library_profile(request, library_id):
  lib = Library.objects.get(id = library_id)
  lab = LabGroup.objects.get(lab_name = lib.lab_name)
  s = Spectra.objects.filter(library__exact = lib)
  return render(
      request,
      'chat/library_profile.html',
      {'library': lib, 'lab': lab, 'spectra': s}
  )

def lab_profile(request, lab_id):
  '''View profile of lab with lab_name'''
  lab = LabGroup.objects.get(id = lab_id)
  return render(request, 'chat/lab_profile.html', {'lab': lab})
  
def spectra_profile(request, spectra_id):
  
  spectra = Spectra.objects.get(id = spectra_id)
  return render(request, 'chat/spectra_profile.html', {'spectra': spectra})

@login_required
def edit_metadata(request, strain_id):
      
  if request.method == "POST":
    # instance kwargs passed in sets the user on the modelForm
    form = MetadataForm(request.POST, request.FILES, instance = Metadata.objects.get(strain_id = strain_id))
    if form.is_valid():
      form.save()
      return redirect(reverse('chat:view_metadata', args = (strain_id, )))
  else:
    form = MetadataForm(instance = XML.objects.get(strain_id = strain_id))
  return render(request, 'chat/edit_metadata.html', {'form': form})

@login_required
def edit_xml(request, xml_hash):
  ''' edit details of xml'''    
  if request.method == "POST":
    # instance kwargs passed in sets the user on the modelForm
    form = XmlForm(request.POST, request.FILES, instance = XML.objects.get(xml_hash = xml_hash))
    if form.is_valid():
      form.save()
      return redirect(reverse('chat:view_xml', args = (xml_hash, )))
  else:
    form = XmlForm(instance = XML.objects.get(xml_hash = xml_hash))
  return render(request, 'chat/edit_xml.html', {'form': form})

@login_required
def edit_spectra(request, spectra_id):
  ''' edit details of library '''    
  if request.method == "POST":
    # instance kwargs passed in sets the user on the modelForm
    form = SpectraEditForm(request.POST, request.FILES, instance = Spectra.objects.get(id = spectra_id))
    if form.is_valid():
      form.save()
      return redirect(reverse('chat:view_spectra', args = (lib_id, )))
  else:
    form = SpectraEditForm(instance = Spectra.objects.get(id = spectra_id))
  return render(request, 'chat/edit_spectra.html', {'form': form})

@login_required
def edit_libprofile(request, library_id):
  ''' edit details of library '''    
  if request.method == "POST":
    # instance kwargs passed in sets the user on the modelForm
    form = LibProfileForm(request.POST, request.FILES, instance = Library.objects.get(id = library_id))
    if form.is_valid():
      form.save()
      return redirect(reverse('chat:view_lab', args = (library_id, )))
  else:
    form = LibProfileForm(instance = Library.objects.get(id = library_id))
  return render(request, 'chat/edit_libprofile.html', {'form': form})
    
@login_required
def edit_labprofile(request, lab_id):
  ''' edit profile of lab '''    
  if request.method == "POST":
    # instance kwargs passed in sets the user on the modelForm
    form = LabProfileForm(request.POST, request.FILES,
      instance = LabGroup.objects.get(id = lab_id))
    if form.is_valid():
      form.save()
      return redirect(reverse('chat:view_lab', args = (lab_id, )))
  else:
    form = LabProfileForm(instance = LabGroup.objects.get(id = lab_id))
  return render(request, 'chat/edit_labprofile.html', {'form': form})


@login_required
def add_xml(request):
  if request.method == 'POST':
    form = AddXmlForm(request.POST, request.FILES)
    if form.is_valid():
      entry = form.save(commit = False)
      entry.created_by_id = request.user.id
      entry.save()
      return redirect('chat:home')
  else:
    form = AddXmlForm()
  return render(request, 'chat/add_xml.html', {'form': form})

@login_required
def add_lib(request):
  if request.method == 'POST':
    form = AddLibraryForm(request.POST, request.FILES)
    if form.is_valid():
      entry = form.save(commit = False)
      entry.created_by_id = request.user.id
      entry.save()
      return redirect('chat:home')
  else:
    form = AddLibraryForm()
  return render(request, 'chat/add_lib.html', {'form': form})

@login_required
def add_labgroup(request):
  if request.method == 'POST':
    form = AddLabGroupForm(request.POST, request.FILES)
    if form.is_valid():
      g = form.save(commit = False)
      g.user = request.user
      g.created_by_id = request.user.id
      g.save() # first save before using the m2m owners rel.
      g.owners.add(request.user)
      g.save()
      return redirect('chat:home')
  else:
    form = AddLabGroupForm()
  return render(request, 'chat/add_labgroup.html', {'form': form})
  
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
  return render(request, 'chat/add_post.html', {'form': form})

@login_required
def add_metadata(request):
  ''' create a new posts to user '''
  if request.method == 'POST':
    form = MetadataForm(request.POST, request.FILES)
    if form.is_valid():
      md = form.save(commit = False)
      md.user = request.user
      md.created_by_id = request.user.id
      md.save()
      return redirect('chat:home')
  else:
    form = MetadataForm()
  return render(request, 'chat/add_metadata.html', {'form': form})

@login_required
@require_POST
def add_comment(request, post_id):
  ''' Add a comment to a post '''
  form = CommentForm(request.POST)
  if form.is_valid():
    # pass the post id to the comment save() method which was overriden
    # in the CommentForm implementation
    comment = form.save(Spectra.objects.get(id = post_id), request.user)
  return redirect(reverse('chat:home'))

def simple_list(request):
  queryset = Library.objects.all()
  table = SimpleTable(queryset)
  return render(request, 'chat/simple_list.html', {'table': table})

from django_tables2 import MultiTableMixin
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name = 'dispatch')
class LibCollapseListView(MultiTableMixin, TemplateView):
  model = Library
  table_class = LibCollapseTable
  template_name = 'chat/collapse_library.html'  
  tables = []
  
  def get_context_data(self, **kwargs):
    #context = super(SearchResultsView, self).get_context_data(**kwargs)
    context = super().get_context_data(**kwargs)
     
    initial = {
      'library': self.request.GET.get('library', None),
      'peak_percent_presence':
          self.request.GET.get('peak_percent_presence', '70.0'),
      'min_snr': self.request.GET.get('min_snr', '0.25'),
      'tolerance': self.request.GET.get('tolerance', '0.002'),
      'collapse_types': self.request.GET.get('spectra_content', 'all'),
    }
    form = LibraryCollapseForm(initial)
    from django.db.models import Count
    if form.is_valid():
      print('lcf valid')
      qs_sm = Spectra.objects.raw(
        'SELECT 1 as id, s.strain_id as "strain_id", '
          'COUNT(s.strain_id) AS "num_replicates" '
        'FROM chat_spectra s '
        'LEFT OUTER JOIN '
          'chat_metadata m ON (s.strain_id = m.id) '
        'WHERE s.library_id = {} AND s.max_mass > 6000'
        'GROUP BY s.strain_id' \
        .format(form.cleaned_data['library'].id)
      )
      print('lcf valid')
      qs_pr = Spectra.objects.raw(
        'SELECT 1 as id, s.strain_id as "strain_id", '
          'COUNT(s.strain_id) AS "num_replicates" '
        'FROM chat_spectra s '
        'LEFT OUTER JOIN '
          'chat_metadata m ON (s.strain_id = m.id) '
        'WHERE s.library_id = {} AND s.max_mass < 6000'
        'GROUP BY s.strain_id' \
        .format(form.cleaned_data['library'].id)
      ) 
        
      self.tables = [
        LibCollapseTable(qs_sm),
        LibCollapseTable(qs_pr),# exclude = ("country", ))
      ]
      
    context.update({
      'form': form,
      'tables': self.tables,
    })
    
    return context
    
  def get_queryset(self):
    print('LibCollapseListView:get_queryset')
    pass
    
    try:
      li = Library.objects.get(
        id = self.request.GET.get('library', None)
      )
    except Library.DoesNotExist:
      li = None
      
    initial = {
      'library': li,
      'peak_percent_presence':
          self.request.GET.get('peak_percent_presence', '70.0'),
      'min_snr': self.request.GET.get('min_snr', '0.25'),
      'tolerance': self.request.GET.get('tolerance', '0.002'),
      'collapse_types': self.request.GET.get('spectra_content', 'all'),
    }
    form = LibraryCollapseForm(initial)
    if form.is_valid() is False:
      print('lcf invalid')
    elif form.is_valid():
      print('lcf valid')
      qs = Spectra.objects.filter(
        library__exact = form.cleaned_data['library']
      )
      qs_sm = qs.filter(max_mass__lt = 6000) \
        .group_by('strain_id') \
        .annotate(num_replicates = Count('strain_id')) \
        .order_by('strain_id')
      qs_pr = qs.filter(max_mass__gt = 6000) \
        .group_by('strain_id') \
        .annotate(num_replicates = Count('strain_id')) \
        .order_by('strain_id')
      self.tables = [
        LibCollapseTable(qs_sm),
        LibCollapseTable(qs_pr),# exclude = ("country", ))
      ]
      return self.queryset

def preview_collapse_lib(request):
  '''Preview collapse of library's replicates'''
  
  # ~ try:
    # ~ initial['library'] = Library.objects.get(
      # ~ id = request.GET.get('library', None)
    # ~ )
  # ~ except Library.DoesNotExist:
    # ~ pass    
  # ~ lib = Library.objects.get(id = lib_id)
  # ~ spectra = Spectra.objects.filter(library = lib)
  # ~ md = Metadata.objects.filter(library = lib)
  #if request.method == "POST":
  #  form = LibraryCollapseForm(request.POST, request.FILES)
  #    # ~ instance = Library.objects.get(id = lib_id))
  #  if form.is_valid():
  #    form.save()
  #    return redirect(reverse('chat:home'))
  #    # ~ return redirect(reverse('chat:view_metadata', args = (lib_id, )))
  # ~ else:
    
  return render(request, 'chat/collapse_library.html', {'form': form})
  
  # ~ return render(
      # ~ request,
      # ~ 'chat/collapse_library.html',
      # ~ #{'library': lib, 'spectra': spectra, 'metadata': md, 'form': form}
      # ~ {'form': form}
  # ~ )
  
class SearchResultsView(ListView):
  model = Spectra
  template_name = 'chat/search_results.html'
  
  def get_context_data(self, **kwargs):
    context = super(SearchResultsView, self).get_context_data(**kwargs)
    context.update({
      'unique_strains': Metadata.objects.order_by().values('strain_id').distinct()
    })
    return context

  def get_queryset(self):
    # all spectra from a given strain_id
    strain_id = self.request.GET.get('strain_id')
    object_list = Spectra.objects.filter(
      strain_id__strain_id__exact = strain_id
    )
    return object_list

class UserTaskListView(SingleTableView):
  model = UserTask
  table_class = UserTaskTable
  template_name = 'chat/user_tasks.html'
  
  def get_queryset(self, *args, **kwargs):
    return UserTask.objects.filter(owner = self.request.user) \
      .order_by('-last_modified') #statuses__status_date
    
class XmlListView(SingleTableView):
  model = XML
  table_class = XmlTable
  template_name = 'chat/xml.html'

class LibrariesListView(SingleTableView):
  model = Library
  table_class = LibraryTable
  template_name = 'chat/libraries.html'
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['table'].table_type = 'libraries'
    return context

def view_cosine(request):
  '''API for exploring cosine data
  
  --Returns three objects: binned peaks (list), feature matrix (list),
    cosine scores (matrix)
  '''
  if request.method == 'POST':
    form = ViewCosineForm(request.POST, request.FILES)
    if form.is_valid():
      sc = SpectraScores(form).info()
      return render(
        request,
        'chat/view_cosine.html',
        {'form': form, 'sc': sc}
      )
  else:
    print('trace')
    form = ViewCosineForm() #instance = None)
  print('trace2')
  return render(request, 'chat/view_cosine.html', {'form': form})

class SpectraFilter(django_filters.FilterSet):
  library = django_filters.ModelMultipleChoiceFilter(
    queryset = Library.objects.all()
  )
  description = django_filters.CharFilter(lookup_expr = 'icontains')

  class Meta:
    model = Spectra
    exclude = ('id','picture') #fields = ['name', 'price', 'manufacturer']

class FilteredSpectraSearchListView(SingleTableMixin, FilterView):
  '''
  todo: combine filter.form and table
  table: CosineSearchTable
  filter: SpectraFilter
  form: SpectraSearchForm
  '''
  table_class = CosineSearchTable
  model = Spectra
  template_name = 'chat/basic_search.html'
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
        'http://localhost:7001/binPeaks',
        data = payload, headers = headers
      )
      result = r.json() # built-in requests method
      print('result is:', result)
      
      # sort by key
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
      from django.db.models import Case, When
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
  
class FilteredSpectraListView(SingleTableMixin, FilterView):
  table_class = SpectraTable
  model = Spectra
  template_name = 'chat/search_results.html'
  filterset_class = SpectraFilter
  
  def get_queryset(self):
    pass
    
class SpectraListView(SingleTableView):
  model = Spectra
  table_class = SpectraTable
  template_name = 'chat/spectra.html'
  
  def get_queryset(self):
    filter = SpectraFilter(request.GET, queryset = Spectra.objects.all())
    return render(request, 'chat/spectra.html', {'filter': filter})

class MetadataListView(SingleTableView):
  model = Metadata
  table_class = MetadataTable
  template_name = 'chat/metadata.html'

class LabgroupsListView(SingleTableView):
  model = LabGroup
  table_class = LabgroupTable
  template_name = 'chat/labgroups.html'

def search(request):
  return render(request, 'chat/search.html', {'spectra': {}, 'comment_form': {}})
  
def home(request):
  comment_form = CommentForm()
  
  x = XML.objects.all()
  y = Metadata.objects.all()
  y1 = Locale.objects.all()
  y2 = Version.objects.all()
  spectra = Spectra.objects.all()
  lib = Library.objects.all()
  
  countLib = {}
  
  # Stats
  for libInstance in lib.iterator():
    bb = libInstance
    aa = Spectra.objects.filter(library = libInstance.id).count()
    countLib[libInstance.title] = aa
  
  #ib.set
  return render(
    request,
    'chat/home.html',
    {
      'spectra': spectra,
      'comment_form': comment_form,
      'xml': x,
      'metadata': y,
      'locale': y1,
      'version': y2,
      'library': lib,
      'countLib': countLib,
    }
  )

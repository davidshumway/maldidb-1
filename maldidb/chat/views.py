from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from threading import Thread

from django import forms

from .forms import CommentForm, SpectraForm, MetadataForm, \
  LoadSqliteForm, XmlForm, LocaleForm, VersionForm, AddLibraryForm, \
  AddLabGroupForm, AddXmlForm, LabProfileForm, SearchForm, \
  ViewCosineForm, SpectraSearchForm, LibraryCollapseForm, \
  LibProfileForm, SpectraUploadForm, SpectraCollectionsForm

from .models import Spectra, SearchSpectra, SpectraCosineScore, \
  SearchSpectraCosineScore, Metadata, XML, Locale, Version, Library, \
  LabGroup, UserTask, UserTaskStatus, UserFile
  #UserLogs

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


# unused
# ~ from django.contrib.auth import get_user_model
# ~ User = get_user_model()

# Distance measurement
from sklearn.metrics.pairwise import cosine_similarity

# R/json for binning
# ~ from rpy2.robjects import r as R
# ~ import rpy2.robjects as robjects
# ~ print('loaded R')
#import json
#import asyncio

# json and sqlite3 required for sqlite import
import json
import sqlite3

# R
# ~ from rpy2.robjects import r as R
# ~ import rpy2.robjects as robjects
# ~ #from .rfn import R, robjects, SpectraScores
from .rfn import SpectraScores

def start_new_thread(function):
  '''Starts a new thread for long-running tasks'''
  def decorator(*args, **kwargs):
    t = Thread(target = function, args = args, kwargs = kwargs)
    t.daemon = True
    t.start()
    return t
  return decorator

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

  #self.get_result_label(result),
  # ~ def render_to_response(self, context):
    # ~ """Return a JSON response in Select2 format."""
    # ~ q = self.request.GET.get('q', None)
    # ~ create_option = self.get_create_option(context, q)
    # ~ return http.JsonResponse({
      # ~ 'results': self.get_results(context) + create_option,
      # ~ 'pagination': {
        # ~ 'more': self.has_more(context)
      # ~ }
    # ~ })
  
  # ~ def label_from_instance(obj):
    # ~ print(obj)
    # ~ return obj.cKingdom
  
  # ~ def get_create_option(self, context, q):
    ## ~ e.g.,
    ## ~ gco {'paginator': <django.core.paginator.Paginator object at 0x7fc91f02dd90>, 'page_obj': <Page 1 of 297>, 'is_paginated': True, 'object_list': <QuerySet [<Metadata: 1002>, <Metadata: 1004>, <Metadata: 1007>, <Metadata: 1008>, <Metadata: 1009>, <Metadata: 1010>, <Metadata: 1011>, <Metadata: 1012>, <Metadata: 1013>, <Metadata: 1014>]>, 'results': <QuerySet [<Metadata: 1002>, <Metadata: 1004>, <Metadata: 1007>, <Metadata: 1008>, <Metadata: 1009>, <Metadata: 1010>, <Metadata: 1011>, <Metadata: 1012>, <Metadata: 1013>, <Metadata: 1014>]>, 'view': <chat.views.MetadataAutocomplete object at 0x7fc91f02de80>}
    ## ~ gco b
    ## ~ gco []
    # ~ co = super(MetadataAutocomplete, self).get_create_option(context, q)
    # ~ print(f'gco {context}')
    # ~ print(f'gco {q}')
    # ~ print(f'gco {co}')
    # ~ return co
  
  # ~ def get_context_data(self, *args, **kwargs):
    # ~ context = super().get_context_data(*args, **kwargs)
    # ~ print(f'c:{context}')
    # ~ print(f'c:{args}')
    # ~ print(f'c:{kwargs}')
    # ~ return context  
    
#-----------------------------------------------------------------------
# end autocomplete views
#-----------------------------------------------------------------------

@start_new_thread
def preprocess_mzml(file, user_task):
  '''Run R methods to preprocess mzml file
  
  -- add Spectra and update UserFile
  -- example: elt = l.rx2(1) # This is the R `[[`, so one-offset indexing
  -- python docs!
    Python signal handlers are always executed in the main Python thread,
    even if the signal was received in another thread. This means that
    signals can’t be used as a means of inter-thread communication. You
    can use the synchronization primitives from the threading module
    instead. Besides, only the main thread is allowed to set a new
    signal handler.
    e.g., see the article: "Django Anti-Patterns: Signals"

  '''
  result = R['preprocess'](file)
  #print(f'pp result{result}')
  if result.rx2('error'):
    user_task.statuses.add(
      UserTaskStatus.objects.create(
        status = 'error', extra = result.rx2('error'),
        user_task = user_task
    ))
    user_task.statuses.add(
      UserTaskStatus.objects.create(
        status = 'complete', user_task = user_task
    ))
  
  #if result
  #
  

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
        t = UserTask.objects.create(
          owner = request.user,
          task_description = 'preprocess'
        )
        t.statuses.add(UserTaskStatus.objects.create(
          status = 'start', user_task = t))
        preprocess_mzml(str(form.instance.file), t)
        return JsonResponse({'status': 'preprocessing'}, status=200)
      else:
        return JsonResponse({'status': 'ready'}, status=200)
      # optional new thread to preprocess
      # add to library
      
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
def add_sqlite(request):
  '''goes into views.py'''
  if request.method == 'POST':
    form = LoadSqliteForm(request.POST, request.FILES)
    if form.is_valid():
      result = handle_uploaded_file(request, form)
      print('result---', result)
      return redirect('chat:user_tasks')
  else:
    form = LoadSqliteForm()
  return render(request, 'chat/add_sqlite.html', {'form': form})
  
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
      # ~ qs_pr = Spectra.objects.raw(
        # ~ 'SELECT 1 as id, s.strain_id as "strain_id", '
          # ~ 'COUNT(s.strain_id) AS "num_replicates" '
        # ~ 'FROM chat_spectra s '
        # ~ 'LEFT OUTER JOIN chat_metadata m '
          # ~ 'ON (s.strain_id = m.id) '
        # ~ 'WHERE s.library_id = {} AND s.max_mass < 6000'
        # ~ 'GROUP BY s.strain_id' \
        # ~ .format(form.cleaned_data['library'].id)
      # ~ )
      # 'COUNT(c.strain_id) as "num_collapsed" '
      # 'LEFT OUTER JOIN chat_collapsedspectra c '
      # 'ON (s.strain_id in c.strain_id)'
      
      # ~ qs = Metadata.objects.filter(
        # ~ library__exact = form.cleaned_data['library']
      # ~ )
      # ~ qs_sm = qs.annotate('num_replicates' = Count(''))
      
      
      # Works (pr) but doesn't retrieve value of strain_id (only col id)
      # ~ qs = Spectra.objects.filter(
        # ~ library__exact = form.cleaned_data['library']
      # ~ )
      # ~ qs_sm = qs.filter(max_mass__lt = 6000) \
        # ~ .annotate(num_replicates = Count('strain_id')) \
        # ~ .order_by('strain_id')
      # ~ qs_pr = qs.filter(max_mass__gt = 6000) \
        # ~ .values('strain_id') \
        # ~ .annotate(num_replicates = Count('strain_id')) #\
        #.values('strain_id__strain_id') \
      # ~ qs_pr = qs.filter(max_mass__gt = 6000) \
        # ~ .values('strain_id__strain_id') \
        # ~ .annotate(num_replicates = Count('strain_id')) #\
        # ~ #, num_replicates = Count('strain_id')) #\
        # ~ #.values('strain_id')# \
        # ~ #.annotate(strain_id = 'strain_id')
        
        
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
  
  # ~ def get(self, *args, **kwargs):
    # ~ resp = super().get(*args, **kwargs)
    # ~ # print(f'get-args: {args}' ) # 
    # ~ # print(f'get-kw: {kwargs}' ) # 
    # ~ return resp
  
  # ~ def post(self, request, *args, **kwargs):

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
    
    # http://127.0.0.1:8000/search/?peak_mass = 1919%2C1939
    # &peak_intensity = 1%2C2&peak_snr = 1%2C2&spectra_file = 
    # &replicates = replicate&spectrum_cutoff = small&preprocessing = processed
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
      
      #sc = SpectraScores()
      #sc.append_spectra(sm, si, sn)
      search_id = obj.id
      
      # small and large molecules combined, or large only
      # use GET query variables to adjust .filter()
      
      n = Spectra.objects.all()
      
      # tof_mode (use min/max instead)
      # ~ if scut == 'small':
        # ~ n = n.filter(tof_mode__exact = 'REFLECTOR')
      # ~ elif scut == 'protein': # protein
        # ~ n = n.filter(tof_mode__exact = 'LINEAR')
      # ~ else: # protein
        # ~ pass
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
      
      # ~ try:
          # ~ ...
      # ~ except json.JSONDecodeError: # na values in intensity or snr
        # ~ print(spectra.strain_id)
        # ~ print(spectra.peak_snr)        
        # ~ return
        
      search_ids = []
      for spectra in n:
        # ~ sc.append_spectra(
          # ~ spectra.peak_mass, spectra.peak_intensity, spectra.peak_snr
        # ~ )
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
      
      # normal:   -kw: {'data': <QuerySet [
      # Then:
      #  self.table_data = {'extra': '12345'
      # result:   -kw: {'data': {'extra': '12345'
      # overwrite the table data to add some custom data, i.e., the score
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

def handle_uploaded_file(request, tmpForm):
  '''
  Spectra is inserted last as it depends on XML and Metadata tables.
  Requires json and sqlite3 libraries.
  
  Metadata strain_id and XML xml_hash should both be unique but they are 
  not in R01 data?
  '''
  if request.FILES and request.FILES['file']:
    f = request.FILES['file']
    with open('/tmp/test.db', 'wb+') as destination:
      for chunk in f.chunks():
        destination.write(chunk)
    
    # New entry in user's tasks
    t = UserTask.objects.create(
      owner = request.user,
      task_description = 'idbac_sql'
    )
    t.statuses.add(UserTaskStatus.objects.create(status = 'start'))
    thread = idbac_sqlite_insert(request, tmpForm, '/tmp/test.db', t)
    
  elif tmpForm.cleaned_data['upload_type'] == 'all': # hosted on server
    hc = [
      '2019_04_15_10745_db-2_0_0.sqlite',
      '2019_06_06_22910_db-2_0_0.sqlite',
      '2019_06_12_10745_db-2_0_0.sqlite',
      '2019_07_02_22910_db-2_0_0.sqlite',
      '2019_07_10_10745_db-2_0_0.sqlite',
      '2019_07_17_1003534_db-2_0_0.sqlite',
      '2019_09_04_10745_db-2_0_0.sqlite',
      '2019_09_11_1003534_db-2_0_0.sqlite',
      '2019_09_18_22910_db-2_0_0.sqlite',
      '2019_09_25_10745_db-2_0_0.sqlite',
      '2019_10_10_1003534_db-2_0_0.sqlite',
      '2019_11_13_1003534_db-2_0_0.sqlite',
      '2019_11_20_1003534_db-2_0_0.sqlite',
    ]
    for f in hc:
      # New entry in user's tasks
      t = UserTask.objects.create(
        owner = request.user,
        task_description = 'idbac_sql'
      )
      t.statuses.add(UserTaskStatus.objects.create(status = 'start',
        user_task = t))
      t.statuses.add(
        UserTaskStatus.objects.create(
          status = 'info', extra = 'Loading SQLite file ' + f,
          user_task = t
      ))
      #connection = sqlite3.connect('/home/app/r01data/' + f) # /home/ubuntu/
      idbac_sqlite_insert(request, tmpForm, '/home/app/r01data/' + f, t)
    
@start_new_thread #(args = ('test',)) # args, kwargs
def idbac_sqlite_insert(request, tmpForm, uploadFile, user_task):
  '''
  -- In the case of erroneous data, save the row data to user's
  error log. E.g., if mass, intensity, or snr contain "na" or "nan".
  -- Wrap entire insert in try-catch, noting errors for 
  later inspection.
  '''  
  try:
    _idbac_sqlite_insert(request, tmpForm, uploadFile, user_task)
  except Exception as e:
    user_task.statuses.add(
      UserTaskStatus.objects.create(
        status = 'error',
        extra = 'Unexpected except caught\n{}: {}'.format(type(e).__name__, e),
        user_task = user_task
    ))
  finally:
    user_task.statuses.add(
      UserTaskStatus.objects.create(
        status = 'complete', user_task = user_task
    ))
  
    # ~ UserLogs.objects.create(
      # ~ owner = request.user,
      # ~ title = 'Peak mass, intensity, or SNR contains an "NA" value',
      # ~ description = 'Row data:' + json.dumps(data),
    # ~ )
    # ~ data_error = True

def _idbac_sqlite_insert(request, tmpForm, uploadFile, user_task):
  
  idbac_version = '1.0.0'
  connection = sqlite3.connect(uploadFile)
  cursor = connection.cursor()
  # ~ data_error = False # Save this value to UserTasks
  
  # Version
  rows = cursor.execute("SELECT * FROM version").fetchall()
  for row in rows:
    idbac_version = row[2] if len(row) == 3 else '1.0.0'
    data = {
      'idbac_version': row[0],
      'r_version': row[1],
      'db_version': idbac_version,
    }
    form = VersionForm(data)
    if form.is_valid():
      entry = form.save(commit = False)
      entry.save()
    else:
        raise ValueError('xxxxx')
        
  # Metadata
  user_task.statuses.add(
    UserTaskStatus.objects.create(
      status = 'info', extra = 'Inserting metadata',
      user_task = user_task
  ))
  
  rows = cursor.execute("SELECT * FROM metaData").fetchall()
  for row in rows:
    data = {
      'strain_id': row[0],
      'genbank_accession': row[1],
      'ncbi_taxid': row[2],
      'cKingdom': row[3],
      'cPhylum': row[4],
      'cClass': row[5],
      'cOrder': row[6],
      'cGenus': row[7],
      'cSpecies': row[8],
      'maldi_matrix': row[9],
      'dsm_cultivation_media': row[10],
      'cultivation_temp_celsius': row[11],
      'cultivation_time_days': row[12],
      'cultivation_other': row[13],
      'user_firstname_lastname': row[14],
      'user_orcid': row[15],
      'pi_firstname_lastname': row[16],
      'pi_orcid': row[17],
      'dna_16s': row[18],
      'created_by': request.user.id,
      'library': tmpForm.cleaned_data['library'].id,
      'lab_name': tmpForm.cleaned_data['lab_name'].id,
    }
    form = MetadataForm(data)
    
    if form.is_valid():
      entry = form.save(commit = False)
      entry.save()
    # ~ form_is_valid = await sync_to_async(form.is_valid)()
    # ~ await sync_to_async(entry.save)()
    else:
      print(form.errors)
      raise ValueError('xxxxx')
  
  # XML
  user_task.statuses.add(
    UserTaskStatus.objects.create(
      status = 'info', extra = 'Inserting XML', user_task = user_task
  ))
  rows = cursor.execute("SELECT * FROM XML").fetchall()
  for row in rows:
    data = {
      'xml_hash': row[0],
      'xml': row[1],
      'manufacturer': row[2],
      'model': row[3],
      'ionization': row[4],
      'analyzer': row[5],
      'detector': row[6],
      'instrument_metafile': row[7],
      'created_by': request.user.id,
      'library': tmpForm.cleaned_data['library'].id,
      'lab_name': tmpForm.cleaned_data['lab_name'].id,
    }
    form = XmlForm(data)
    if form.is_valid():
      entry = form.save(commit = False)
      entry.save()
    else:
      form.non_field_errors()
      field_errors = [ (field.label, field.errors) for field in form] 
      raise ValueError('xxxxx')
  
  # Locale
  rows = cursor.execute("SELECT * FROM locale").fetchall()
  for row in rows:
    data = {
      'locale': row[0],
    }
    form = LocaleForm(data)
    if form.is_valid():
      entry = form.save(commit = False)
      entry.save()
    else:
        raise ValueError('xxxxx')
    
  # Spectra
  # row[5] spectrumIntensity ??
  user_task.statuses.add(
    UserTaskStatus.objects.create(
      status = 'info', extra = 'Inserting spectra',
      user_task = user_task
  ))
  t = 'IndividualSpectra' if idbac_version == '1.0.0' else 'spectra'
  rows = cursor.execute('SELECT * FROM '+t).fetchall()
  for row in rows:
    
    sxml = XML.objects.filter(xml_hash = row[2])
    if sxml:
      sxml = sxml[0]
    smd = Metadata.objects.filter(strain_id = row[3])
    if smd:
      smd = smd[0]
    
    pm = json.loads(row[4])
    
    data = {
      'created_by': request.user.id,
      'library': tmpForm.cleaned_data['library'].id,
      'lab_name': tmpForm.cleaned_data['lab_name'].id,
      'privacy_level': tmpForm.cleaned_data['privacy_level'][0],
      
      'spectrum_mass_hash': row[0],
      'spectrum_intensity_hash': row[1],
      
      'xml_hash': sxml.id,
      'strain_id': smd.id,
      'peak_mass': ",".join(map(str, pm['mass'])),
      'peak_intensity': ",".join(map(str, pm['intensity'])),
      'peak_snr': ",".join(map(str, pm['snr'])),
      
      'max_mass': row[6],
      'min_mass': row[7],
      'spot': row[36]
    }
    
    # Sanity check ("na" or "nan"): Skip this row.
    if 'na' in row[4].lower():
      user_task.statuses.add(
        UserTaskStatus.objects.create(
          status = 'error',
          extra = 'Peak mass, intensity, or SNR contains an "NA" value:\n\n'
            'Row data:\n\n' + json.dumps(data),
          user_task = user_task
      ))
      continue
    
    form = SpectraForm(data)
    if form.is_valid():
      entry = form.save(commit = False)
      entry.save()
    else:
      form.non_field_errors()
      field_errors = [ (field.label, field.errors) for field in form] 
      raise ValueError('xxxxx')
  
  # Close the db connection  
  from django.db import connection
  connection.close()


def search(request):
  
  return render(request, 'chat/search.html', {'spectra': {}, 'comment_form': {}})
  
def home(request):
  ''' The home news feed page '''

  # Get users whose posts to display on news feed and add users account
  # ~ users = list(request.user.followers.all())
  # ~ users.append(request.user)

  # Get posts from users accounts whose posts to display and order by latest
  #posts = Post.objects.filter(user__in = users).order_by('-posted_date')
  comment_form = CommentForm()
  
  x = XML.objects.all()
  y = Metadata.objects.all()
  y1 = Locale.objects.all()
  y2 = Version.objects.all()
  spectra = Spectra.objects.all()
  lib = Library.objects.all()
  
  countLib = {}
  #distinctPostLibs = Post.objects.distinct('library')
  
  # Some stats for each library
  # Num spectra per library
  # Num species per library
  for libInstance in lib.iterator():
    bb = libInstance
    aa = Spectra.objects.filter(library = libInstance.id).count()
    countLib[libInstance.title] = aa
    #libInstance.pie = 1
    #lib[i]['asdf'] = 1
  
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


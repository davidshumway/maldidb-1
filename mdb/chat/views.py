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

from .tables import *

import django_filters
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import SingleTableView
import django_tables2 as tables

from mdb.utils import *

import requests

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
    
@login_required
def collapse_library(request, lib_id):
  ''''''    
  if request.method == 'GET':
    try:
      lib = Library.objects.get(pk = lib_id)
    except Library.DoesNotExist:
      return redirect(reverse('chat:libraries_results'))
      # ~ Library not found
    if lib not in Library.objects.filter(created_by = request.user):
      return redirect(reverse('chat:libraries_results'))
      # ~ You are not the owner of that library
    # Valid. Collapse and redirect.
    BgProcess.collapse_lib(id = lib_id, owner = request.user)
    return redirect(reverse('chat:user_tasks'))
  else:
    return render(request, 'chat/libraries.html')
  
@method_decorator(login_required, name = 'dispatch')
class LibCollapseListView(MultiTableMixin, TemplateView):
  '''
  -- This uses a class-based login decorator
  '''
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
  
  Returns three objects: binned peaks (list), feature matrix (list),
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
    form = ViewCosineForm() #instance = None)
  return render(request, 'chat/view_cosine.html', {'form': form})

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

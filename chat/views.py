from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from django import forms

from .forms import CommentForm
from .forms import SpectraForm
from .forms import MetadataForm
from .forms import LoadSqliteForm
from .forms import XmlForm
from .forms import LocaleForm
from .forms import VersionForm
from .forms import AddLibraryForm
from .forms import AddLabGroupForm
from .forms import AddXmlForm
from .forms import LabProfileForm
from .forms import SearchForm
from .forms import ViewCosineForm
from .forms import SpectraSearchForm

from .models import Spectra
from .models import SearchSpectra
from .models import SpectraCosineScore
from .models import SearchSpectraCosineScore
from .models import Metadata
from .models import XML
from .models import Locale
from .models import Version
from .models import Library
from .models import LabGroup

from django.db.models import Q
from django.views.generic import TemplateView, ListView

from .tables import LibraryTable, SpectraTable, MetadataTable, LabgroupTable, CosineSearchTable, XmlTable

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
from rpy2.robjects import r as R
import rpy2.robjects as robjects
print('loaded R')
import json


def preview_collapse_lib(request, lib_id):
  """Preview a collapse of library replicates"""
  lib = Library.objects.get(id=lib_id)
  spectra = Spectra.objects.filter(library=lib)
  md = Metadata.objects.filter(library=lib)
  return render(
      request,
      'chat/preview_collapse_lib.html',
      {'library': lib, 'spectra': spectra, 'metadata': md}
  )

def metadata_profile(request, strain_id):
  """"""
  md = Metadata.objects.get(strain_id=strain_id)
  return render(
      request,
      'chat/metadata_profile.html',
      {'metadata': md}
  )

def xml_profile(request, xml_hash):
  """"""
  xml = XML.objects.get(xml_hash=xml_hash)
  lab = LabGroup.objects.get(lab_name=xml.lab_name)
  return render(
      request,
      'chat/xml_profile.html',
      {'xml': xml, 'lab': lab}
  )

def library_profile(request, library_id):
  """"""
  lib = Library.objects.get(id=library_id)
  lab = LabGroup.objects.get(lab_name=lib.lab_name)
  s = Spectra.objects.filter(library__exact=lib)
  return render(
      request,
      'chat/library_profile.html',
      {'library': lib, 'lab': lab, 'spectra': s}
  )

def lab_profile(request, lab_id):
  """View profile of lab with lab_name"""
  lab = LabGroup.objects.get(id=lab_id)
  return render(request, 'chat/lab_profile.html', {'lab': lab})
  
def spectra_profile(request, spectra_id):
  """"""
  spectra = Spectra.objects.get(id=spectra_id)
  return render(request, 'chat/spectra_profile.html', {'spectra': spectra})

@login_required
def edit_metadata(request, strain_id):
  """"""    
  if request.method == "POST":
    # instance kwargs passed in sets the user on the modelForm
    form = MetadataForm(request.POST, request.FILES, instance=Metadata.objects.get(strain_id=strain_id))
    if form.is_valid():
      form.save()
      return redirect(reverse('chat:view_metadata', args=(strain_id, )))
  else:
    form = MetadataForm(instance=XML.objects.get(strain_id=strain_id))
  return render(request, 'chat/edit_metadata.html', {'form': form})

@login_required
def edit_xml(request, xml_hash):
  """ edit details of xml"""    
  if request.method == "POST":
    # instance kwargs passed in sets the user on the modelForm
    form = XmlForm(request.POST, request.FILES, instance=XML.objects.get(xml_hash=xml_hash))
    if form.is_valid():
      form.save()
      return redirect(reverse('chat:view_xml', args=(xml_hash, )))
  else:
    form = XmlForm(instance=XML.objects.get(xml_hash=xml_hash))
  return render(request, 'chat/edit_xml.html', {'form': form})

@login_required
def edit_spectra(request, spectra_id):
  """ edit details of library """    
  if request.method == "POST":
    # instance kwargs passed in sets the user on the modelForm
    form = SpectraEditForm(request.POST, request.FILES, instance=Spectra.objects.get(id=spectra_id))
    if form.is_valid():
      form.save()
      return redirect(reverse('chat:view_spectra', args=(lib_id, )))
  else:
    form = SpectraEditForm(instance=Spectra.objects.get(id=spectra_id))
  return render(request, 'chat/edit_spectra.html', {'form': form})

@login_required
def edit_libprofile(request, lib_id):
  """ edit details of library """    
  if request.method == "POST":
    # instance kwargs passed in sets the user on the modelForm
    form = LibProfileForm(request.POST, request.FILES, instance=Library.objects.get(id=lib_id))
    if form.is_valid():
      form.save()
      return redirect(reverse('chat:view_lab', args=(lib_id, )))
  else:
    form = LibProfileForm(instance=Library.objects.get(id=lib_id))
  return render(request, 'chat/edit_libprofile.html', {'form': form})
    
@login_required
def edit_labprofile(request, lab_id):
  """ edit profile of lab """    
  if request.method == "POST":
    # instance kwargs passed in sets the user on the modelForm
    form = LabProfileForm(request.POST, request.FILES, instance=LabGroup.objects.get(id=lab_id))
    # ~ form = LabProfileForm(request.POST, request.FILES, instance=request.user.profile)
    if form.is_valid():
      form.save()
      return redirect(reverse('chat:view_lab', args=(lab_id, )))
      # ~ return redirect(reverse('chat:view_lab', args=(request.lab.id, )))
  else:
    # ~ import pprint
    # ~ pp = pprint.PrettyPrinter(indent=4)
    # ~ pp.pprint(request)
    # ~ print(request.user)
    # ~ print(request)
    # ~ print(request.lab_id)
    form = LabProfileForm(instance=LabGroup.objects.get(id=lab_id))
    # ~ form = LabProfileForm(instance=request.user.profile)
  return render(request, 'chat/edit_labprofile.html', {'form': form})


@login_required
def add_xml(request):
  if request.method == 'POST':
    form = AddXmlForm(request.POST, request.FILES)
    if form.is_valid():
      entry = form.save(commit=False)
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
      entry = form.save(commit=False)
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
      handle_uploaded_file(request, form)
      return redirect('chat:home')
  else:
    form = LoadSqliteForm()
  return render(request, 'chat/add_sqlite.html', {'form': form})
  
@login_required
def add_labgroup(request):
  """"""
  if request.method == 'POST':
    form = AddLabGroupForm(request.POST, request.FILES)
    if form.is_valid():
      g = form.save(commit=False)
      g.user = request.user
      g.created_by_id = request.user.id
      g.save() # first save before using the m2m owners rel.
      g.owners.add(request.user)
      g.save()
      #print(request)
      #print(request.user)
      #print(request.POST) # 'owners': ['1']}
      #print(request.POST['owners'])
      
      return redirect('chat:home')
  else:
    form = AddLabGroupForm()
  return render(request, 'chat/add_labgroup.html', {'form': form})
  
@login_required
def add_post(request):
  """"""
  if request.method == 'POST':
    form = SpectraForm(request.POST, request.FILES)
    if form.is_valid():
      post = form.save(commit=False)
      post.user = request.user
      post.created_by_id = request.user.id
      post.save()
      return redirect('chat:home')
  else:
    form = SpectraForm()
  return render(request, 'chat/add_post.html', {'form': form})

@login_required
def add_metadata(request):
  """ create a new posts to user """
  if request.method == 'POST':
    form = MetadataForm(request.POST, request.FILES)
    if form.is_valid():
      md = form.save(commit=False)
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
  """ Add a comment to a post """
  form = CommentForm(request.POST)
  if form.is_valid():
    # pass the post id to the comment save() method which was overriden
    # in the CommentForm implementation
    comment = form.save(Spectra.objects.get(id=post_id), request.user)
  return redirect(reverse('chat:home'))


def simple_list(request):
  queryset = Library.objects.all()
  table = SimpleTable(queryset)
  return render(request, 'chat/simple_list.html', {'table': table})

#def search_spectra:
  
  
class SearchResultsView(ListView):
  """"""
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
      # ~ Q(metadata__strain_id__exact = strain_id)
    )
    
    ### All species
    #species_list = Metadata.objects.order_by().values('strain_id').distinct()
    
    return object_list
    #return object_list, species_list
    
  # ~ # Get users whose posts to display on news feed and add users account
  # ~ users = list(request.user.followers.all())
  # ~ users.append(request.user)

  # ~ # Get posts from users accounts whose posts to display and order by latest
  # ~ posts = Post.objects.filter(user__in=_users).order_by('-posted_date')
  # ~ comment_form = CommentForm()
  # ~ return render(request, 'chat/home.html', {'posts': posts, 'comment_form': comment_form})


  # ~ model = Post
  # ~ template_name = 'search_results.html'
  # ~ def get_queryset(self):
  # ~ query = self.request.GET.get('q')
  # ~ object_list = Post.objects.filter(
  # ~ Q(spectraID=query)
  # ~ )
  # ~ return object_list

class XmlListView(SingleTableView):
  model = XML
  table_class = XmlTable
  template_name = 'chat/xml.html'

class LibrariesListView(SingleTableView):
  model = Library
  table_class = LibraryTable
  template_name = 'chat/libraries.html'

R('''
  suppressPackageStartupMessages(library(IDBacApp))
  # Some globals
  allSpectra <- list()
  allPeaks <- list()
  binnedPeaks <- F
  resetGlobal <- function() {
    allSpectra <<- list()
    allPeaks <<- list()
    binnedPeaks <<- F
  }
  appendSpectra <- function(m, i, s) {
    # <<-: assign upward
    # allPeaks: Used for binPeaks, intensityMatrix
    # allSpectra: Used for intensityMatrix
    # todo: createMassPeaks -- snr = as.numeric(x$snr))
    allSpectra <<- append(
      allSpectra,
      MALDIquant::createMassSpectrum(mass=m, intensity=i)
    )
    allPeaks <<- append(
      allPeaks,
      MALDIquant::createMassPeaks(
        mass=m, intensity=i, snr=as.numeric(s)
      )
    )
  }
  binSpectra <- function() {
    print("dims")
    print(dim(allSpectra))
    print(dim(allPeaks))
    # Only scores in first row are relevant, i.e., input spectra
    # Finally, order the row by score decreasing
    binnedPeaks <- MALDIquant::binPeaks(allPeaks, tolerance=0.002)
    print(dim(binnedPeaks))
    featureMatrix <- MALDIquant::intensityMatrix(binnedPeaks, allSpectra)
    print(dim(featureMatrix))
    d <- stats::as.dist(coop::tcosine(featureMatrix))
    d <- as.matrix(d)
    d <- round(d, 3)
    
    # Don't reorder now, leave it to Python
    #d <- d[,order(d[,1],decreasing=T)]
    
    # Discard symmetric part of matrix
    d[lower.tri(d, diag = FALSE)] <- NA
    
    # ~ print(d[1,][0])
    print(d[2,])
    
    d <- d[1,] # first row
  }
  
  # heatmap code
  binSpectraOLD <- function() {
    binnedPeaks <- MALDIquant::binPeaks(allPeaks, tolerance=0.002)
    featureMatrix <- MALDIquant::intensityMatrix(binnedPeaks, allSpectra)
    
    
    # Utilizing: github.com/strejcem/MALDIvs16S/blob/master/R/MALDIbacteria.R
    # ~ similarity <- coop::cosine(t(featureMatrix))
    # ~ d <- as.dist(1-similarity) ### ???
    # ~ d <- as.dist(similarity)
    
    # IDBac: stats::as.dist(1 - coop::tcosine(data))
    # ~ d <- stats::as.dist(1 - coop::tcosine(featureMatrix))
    d <- stats::as.dist(coop::tcosine(featureMatrix))
    
    
    x <- as.matrix(d)
    x <- round(x, 2)
    #print('d')
    #print(d)
    
    #jpeg(file="test.jpg", quality=100, width=2000, height=2000)
    png(file="test.png", width=3000, height=3000, res=300, pointsize=6)
    # ~ heatmap(d) #, col = palette, symm = TRUE)
    # ~ heatmap(as.matrix(d[, -1])) #, col = palette, symm = TRUE)
    heatmap(x, symm = FALSE, Colv = NA, Rowv = NA) #, col = palette, symm = TRUE)
    # ~ heatmap.2(as.matrix(d), symm = FALSE) #, col = palette, symm = TRUE)
    dev.off()
    
    # small section
    png(file="test-sm.png", width=1000, height=1000, res=300, pointsize=6)
    heatmap(x[1:16,1:16], symm = FALSE, Colv = NA, Rowv = NA) #, col = palette, symm = TRUE)
    dev.off()
    
    library(gplots)
    png(file="test2-sm.png", width=1200, height=1200, res=300, pointsize=6)
    gplots::heatmap.2(x[1:16,1:16], symm = FALSE, Colv = NA, Rowv = NA, cellnote=x[1:16,1:16], notecex=0.5, trace="none")
    dev.off()
    
    png(file="test2-med.png", width=1200, height=1200, res=300, pointsize=6)
    gplots::heatmap.2(x[1:32,1:32], symm = FALSE, Colv = NA, Rowv = NA, cellnote=x[1:32,1:32], notecex=0.5, trace="none")
    dev.off()
    
    png(file="test3-sm.png", width=1200, height=1200, res=300, pointsize=6)
    y <- x
    y[lower.tri(x, diag = FALSE)] <- NA
    gplots::heatmap.2(y[1:16,1:16], symm = FALSE, Colv = NA, Rowv = NA, cellnote=y[1:16,1:16], notecex=0.5, trace="none")
    dev.off()
    
    png(file="test3-med.png", width=1200, height=1200, res=300, pointsize=6)
    y <- x
    y[lower.tri(x, diag = FALSE)] <- NA
    gplots::heatmap.2(y[1:32,1:32], symm = FALSE, Colv = NA, Rowv = NA, cellnote=y[1:32,1:32], notecex=0.5, trace="none")
    dev.off()
    
    png(file="test3-full.png", width=3000, height=3000, res=300, pointsize=6)
    y <- x
    y[lower.tri(x, diag = FALSE)] <- NA
    gplots::heatmap.2(y, symm = FALSE, Colv = NA, Rowv = NA, trace="none")
    dev.off()
    
    
    png(file="test4-sm.png", width=1200, height=1200, res=300, pointsize=6)
    y <- x
    y[y == 0] <- 1
    gplots::heatmap.2(y[1:16,1:16], symm = FALSE, cellnote=y[1:16,1:16], notecex=0.5, trace="none")
    dev.off()
    
    png(file="test4-med.png", width=1200, height=1200, res=300, pointsize=6)
    y <- x
    y[y == 0] <- 1
    gplots::heatmap.2(y[1:32,1:32], symm = FALSE, cellnote=y[1:32,1:32], notecex=0.5, trace="none")
    dev.off()
    
    png(file="test4-full.png", width=3000, height=3000, res=300, pointsize=6)
    y <- x
    y[y == 0] <- 1
    gplots::heatmap.2(y, symm = FALSE, trace="none")
    dev.off()
    
  }
''')

def view_cosine(request):
  """ edit profile of lab """
  # small and large molecules combined, or large only
  print('start adding')
  # ~ n = Spectra.objects.all()
  n = Spectra.objects.all().filter(tof_mode__exact='LINEAR').order_by('xml_hash')
  for spectra in n:
    pm = json.loads('['+spectra.peak_mass+']')
    pi = json.loads('['+spectra.peak_intensity+']')
    R['appendSpectra'](
      robjects.FloatVector(pm),
      robjects.FloatVector(pi)
    )
  print('end adding')
  print('start binning')
  R['binSpectra']()
  print('end binning')
  
  
  if request.method == "POST":
    form = ViewCosineForm(request.POST, request.FILES, instance=None)
    if form.is_valid():
      #form.save()
      
      return redirect(reverse('chat:view_cosine'))
  else:
    form = ViewCosineForm(instance=None)
  return render(request, 'chat/view_cosine.html', {'form': form})

class SpectraFilter(django_filters.FilterSet):
  library = django_filters.ModelMultipleChoiceFilter(
    queryset = Library.objects.all()
    #, to_field_name="title",
    #required = False
  )

  description = django_filters.CharFilter(lookup_expr='icontains')

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
  
  # ~ def form_valid(self, form):
    # ~ form.instance.library_id = self.kwargs.get('pk')
    # ~ return super(FilteredSpectraSearchListView, self).form_valid(form)

  def get_context_data(self, **kwargs):
    '''Render filter widget to pass to the table template.
    '''
    context = super().get_context_data(**kwargs)

    f = SpectraFilter(self.request.GET, queryset=self.queryset)
    context['filter'] = f
    # ~ print('filter form', f)
    
    for attr, field in f.form.fields.items():
      context['table'].columns[attr].w = field.widget.render(attr, '')
      # ~ print(attr, field)
      # ~ for attr2, value2 in value.__dict__.items():
        # ~ widget = value2.widget
        # ~ context['table'].columns[widget.name] = widget.render()
        # ~ print(attr2, value2)
        # ~ pass
    
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
    
    print(f'gg: {self.request.GET}' ) # 
    print(f'gg: {self.request.GET.get("peak_mass")}' ) # 
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
        if tag not in secondary_top:
          boundField = forms.forms.BoundField(form, form.fields[tag], tag)
          secondary_form.append(boundField)
        else: # Prepend, add to index=0
          boundField = forms.forms.BoundField(form, form.fields[tag], tag)
          boundField.label = boundField.label.replace('xx', '')
          secondary_form.insert(0, boundField)
    
    context['form'] = form
    context['secondary_form_fields'] = secondary_form
    
    return context
  
  def get(self, *args, **kwargs):
    resp = super().get(*args, **kwargs)
    # ~ print(f'get-args: {args}' ) # 
    # ~ print(f'get-kw: {kwargs}' ) # 
    return resp
  
  # ~ def post(self, request, *args, **kwargs):

  def get_queryset(self, *args, **kwargs):
    '''calling queryset.update does not update the model.'''
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
    
    # http://127.0.0.1:8000/search/?peak_mass=1919%2C1939
    # &peak_intensity=1%2C2&peak_snr=1%2C2&spectra_file=
    # &replicates=replicate&spectrum_cutoff=small&preprocessing=processed
    sm = form.cleaned_data['peak_mass'];
    si = form.cleaned_data['peak_intensity'];
    sn = form.cleaned_data['peak_snr'];
    srep = form.cleaned_data['replicates'];
    scut = form.cleaned_data['spectrum_cutoff'];
    if sm and si and sn and srep and scut:
      print('valid data')
      self.show_tbl = True
      
      # reset R globals
      R['resetGlobal']()
      
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
      R['appendSpectra'](
        robjects.FloatVector(json.loads('[' + sm + ']')),
        robjects.FloatVector(json.loads('[' + si + ']')),
        robjects.FloatVector(json.loads('[' + sn + ']'))
      )
      
      # small and large molecules combined, or large only
      # use GET query variables to adjust .filter()
      
      n = Spectra.objects.all()
      
      if scut == 'small':
        n = n.filter(tof_mode__exact='REFLECTOR')
      elif scut == 'protein': # protein
        n = n.filter(tof_mode__exact='LINEAR')
      else: # protein
        pass
      
      # optionals
      slib = form.cleaned_data['libraryXX']; #in
      # ~ sprv = form.cleaned_data['privacy_level'];
      slab = form.cleaned_data['lab_nameXX'];
      ssid = form.cleaned_data['strain_idXX'];
      sxml = form.cleaned_data['xml_hashXX'];
      scrb = form.cleaned_data['created_byXX'];
      print(f'fcd: {form.cleaned_data}' ) # 
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
      # ~ print(n)
      
      idx = {}
      count = 0
      for spectra in n:
        pm = json.loads('['+spectra.peak_mass+']')
        pi = json.loads('['+spectra.peak_intensity+']')
        ps = json.loads('['+spectra.peak_snr+']')
        R['appendSpectra'](
          robjects.FloatVector(pm),
          robjects.FloatVector(pi),
          robjects.FloatVector(ps)
        )
        idx[count] = spectra
        count += 1
      result = R['binSpectra']()
      
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
      
      sorted_list.sort(key=sort_func, reverse=True)
      
      pk_list = [key.get('id') for key in sorted_list]
      
      from django.db.models import Case, When
      preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
      q = Spectra.objects.filter(id__in=pk_list).order_by(preserved)
      
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
    filter = SpectraFilter(request.GET, queryset=Spectra.objects.all())
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
  not in R01 data.
    get() returned more than one Metadata -- it returned 2!
    e.g, smd = ...get(strain_id=row[3])
  '''
  import json
  import sqlite3
  
  if request.FILES and request.FILES['file']:
    f = request.FILES['file']
    with open('/tmp/test.db', 'wb+') as destination:
      for chunk in f.chunks():
        destination.write(chunk)
    connection = sqlite3.connect('/tmp/test.db')
    idbac_sqlite_insert(request, tmpForm, connection)
  elif tmpForm.cleaned_data['upload_type'] == 'all': # hosted on server
    hc = [
      '2019_04_15_10745_db-2_0_0.sqlite',
      '2019_07_02_22910_db-2_0_0.sqlite',
      '2019_09_11_1003534_db-2_0_0.sqlite',
      '2019_10_10_1003534_db-2_0_0.sqlite',
      '2019_06_06_22910_db-2_0_0.sqlite',
      '2019_06_06_22910_db-2_0_0.sqlite',
      '2019_09_18_22910_db-2_0_0.sqlite',
      '2019_11_13_1003534_db-2_0_0.sqlite',
      '2019_06_12_10745_db-2_0_0.sqlite',
      '2019_09_04_10745_db-2_0_0.sqlite',
      '2019_09_25_10745_db-2_0_0.sqlite',
      '2019_11_20_1003534_db-2_0_0.sqlite',
    ]
    for f in hc:
      connection = sqlite3.connect('/home/ubuntu/' + f)
      idbac_sqlite_insert(request, tmpForm, connection)
    
  
def idbac_sqlite_insert(request, tmpForm, connection):
    
  cursor = connection.cursor()
  
  # Metadata
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
      'library': tmpForm.cleaned_data['library'][0].id,
      'lab_name': tmpForm.cleaned_data['lab_name'][0].id,
    }
    form = MetadataForm(data)
    if form.is_valid():
      entry = form.save(commit=False)
      entry.save()
    else:
      print(form.errors)
      raise ValueError('xxxxx')
  
  # XML
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
      # ~ 'created_by': tmpForm.cleaned_data['user'][0].id,
      'library': tmpForm.cleaned_data['library'][0].id,
      'lab_name': tmpForm.cleaned_data['lab_name'][0].id,
    }
    form = XmlForm(data)
    if form.is_valid():
      entry = form.save(commit=False)
      entry.save()
    else:
      form.non_field_errors()
      field_errors = [ (field.label, field.errors) for field in form] 
      raise ValueError('xxxxx')
  
  # Version
  rows = cursor.execute("SELECT * FROM version").fetchall()
  for row in rows:
    data = {
      'idbac_version': row[0],
      'r_version': row[1],
      'db_version': row[2],
    }
    form = VersionForm(data)
    if form.is_valid():
      entry = form.save(commit=False)
      entry.save()
    else:
        raise ValueError('xxxxx')
  
  # Locale
  rows = cursor.execute("SELECT * FROM locale").fetchall()
  for row in rows:
    data = {
      'locale': row[0],
    }
    form = LocaleForm(data)
    if form.is_valid():
      entry = form.save(commit=False)
      entry.save()
    else:
        raise ValueError('xxxxx')
    
  
  # Spectra
  rows = cursor.execute("SELECT * FROM spectra").fetchall()
  for row in rows:
    
    sxml = XML.objects.filter(xml_hash=row[2])
    if sxml:
      sxml = sxml[0]
    smd = Metadata.objects.filter(strain_id=row[3])
    if smd:
      smd = smd[0]
    
    pm = json.loads(row[4])

    data = {
      'created_by': request.user.id,
      'library': tmpForm.cleaned_data['library'][0].id,
      'lab_name': tmpForm.cleaned_data['lab_name'][0].id,
      
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
      'ignore': row[8],
      'number': row[9],
      'time_delay': row[10],
      'time_delta': row[11],
      'calibration_constants': row[12],
      'v1_tof_calibration': row[13],
      'data_type': row[14],
      'data_system': row[15],
      'spectrometer_type': row[16],
      'inlet': row[17],
      'ionization_mode': row[18],
      'acquisition_method': row[19],
      'acquisition_date': row[20],
      'acquisition_mode': row[21],
      'tof_mode': row[22],
      'acquisition_operator_mode': row[23],
      'laser_attenuation': row[24],
      'digitizer_type': row[25],
      'flex_control_version': row[26],
      'cId': row[27],
      'instrument': row[28],
      'instrument_id': row[29],
      'instrument_type': row[30],
      'mass_error': row[31],
      'laser_shots': row[32],
      'patch': row[33],
      'path': row[34],
      'laser_repetition': row[35],
      'spot': row[36],
      'spectrum_type': row[37],
      'target_count': row[38],
      'target_id_string': row[39],
      'target_serial_number': row[40],
      'target_type_number': row[41],
    }
    form = SpectraForm(data)
    if form.is_valid():
      entry = form.save(commit=False)
      entry.save()
    else:
      form.non_field_errors()
      field_errors = [ (field.label, field.errors) for field in form] 
      raise ValueError('xxxxx')
    


def search(request):
  """ search for spectraID """

  # Get users whose posts to display on news feed and add users account
  users = list(request.user.followers.all())
  users.append(request.user)

  # Get posts from users accounts whose posts to display and order by latest
  posts = Spectra.objects.filter(user__in=users).order_by('-posted_date')
  comment_form = CommentForm()
  return render(request, 'chat/search.html', {'spectra': spectra, 'comment_form': comment_form})
  
def home(request):
  """ The home news feed page """

  # Get users whose posts to display on news feed and add users account
  # ~ users = list(request.user.followers.all())
  # ~ users.append(request.user)

  # Get posts from users accounts whose posts to display and order by latest
  #posts = Post.objects.filter(user__in=users).order_by('-posted_date')
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
    aa = Spectra.objects.filter(library=libInstance.id).count()
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




# TESTING R
try:
  def getRConnection():
    return R
  
  # define an R function
  R('''
    # create a function `f`
    f <- function(r, verbose=FALSE) {
        if (verbose) {
            cat("I am calling f().\n")
        }
        2 * pi * r
    }
    # call the function `f` with argument value 3
    f(3)
    ''')
  print("R['f'](4):", R['f'](4))
  print("R['f'](4) vvv:", R['f'](4, True))
  
  # another one...
  R('''
    collapseReplicates <- function(checkedPool,
                                   sampleIDs,
                                   peakPercentPresence,
                                   lowerMassCutoff,
                                   upperMassCutoff, 
                                   minSNR, 
                                   tolerance = 0.002,
                                   protein){
      
      validate(need(is.numeric(peakPercentPresence), "peakPercentPresence not numeric"))
      validate(need(is.numeric(lowerMassCutoff), "lowerMassCutoff not numeric"))
      validate(need(is.numeric(upperMassCutoff), "upperMassCutoff not numeric"))
      validate(need(is.numeric(minSNR), "minSNR not numeric"))
      validate(need(is.numeric(tolerance), "tolerance not numeric"))
      validate(need(is.logical(protein), "protein not logical"))
      
      
      
      temp <- IDBacApp::getPeakData(checkedPool = checkedPool,
                                    sampleIDs = sampleIDs,
                                    protein = protein) 
      req(length(temp) > 0)
      # Binning peaks lists belonging to a single sample so we can filter 
      # peaks outside the given threshold of presence 
      
      for (i in 1:length(temp)) {
        snr1 <-  which(MALDIquant::snr(temp[[i]]) >= minSNR)
        temp[[i]]@mass <- temp[[i]]@mass[snr1]
        temp[[i]]@snr <- temp[[i]]@snr[snr1]
        temp[[i]]@intensity <- temp[[i]]@intensity[snr1]
      }
      
      specNotZero <- sapply(temp, function(x) length(x@mass) > 0)
      
      # Only binPeaks if spectra(um) has peaks.
      # see: https://github.com/sgibb/MALDIquant/issues/61 for more info 
      # note: MALDIquant::binPeaks does work if there is only one spectrum
      if (any(specNotZero)) {
        
        temp <- temp[specNotZero]
        temp <- MALDIquant::binPeaks(temp,
                                     tolerance = tolerance, 
                                     method = c("strict")) 
        
        temp <- MALDIquant::filterPeaks(temp,
                                        minFrequency = peakPercentPresence / 100) 
        
        temp <- MALDIquant::mergeMassPeaks(temp, 
                                           method = "mean") 
        temp <- MALDIquant::trim(temp,
                                 c(lowerMassCutoff,
                                   upperMassCutoff))
      } else {
        temp <- MALDIquant::mergeMassPeaks(temp, 
                                           method = "mean") 
      }
      
      
      return(temp)
    }
    ''')
    
  pi = R('pi')
  print('pi:',pi[0])
  
  #f <- function(r, verbose=FALSE) {
  R('''    
    toSpectrum <- function(input) {
      if (class(input) == "list") {
        print('list')
        input <- lapply(input, 
          function(x) {
            MALDIquant::createMassSpectrum(
              mass = x[ , 1],
              intensity = x[ , 2])
          })
      } else if (class(input) == "matrix") {
        print('matrix')
        input <- MALDIquant::createMassSpectrum(
          mass = input[ , 1],
          intensity = input[ , 2])
        input <- list(input)
      } # else, dataframe?
      else if (class(input) == "data.frame") {
        #apply(input, 1, fxx) #apply: 1=rows, 2=columns 
        input <- MALDIquant::createMassSpectrum(
          mass = input[ , 1],
          intensity = input[ , 2])
      }
      ###return input
    }
    


    distMatrix <- function(datax, datay,
                           method,
                           booled){
      #data <- toSpectrum(data)
      data <- MALDIquant::createMassSpectrum(
          mass = datax,
          intensity = datay)
      print(data)
      data <- list(data)
      print(nrow(data))
      validate(need(nrow(data) > 2, "Need >2 samples to cluster")) 
      data <- base::as.matrix(data)
      # Change empty to 0
      data[base::is.na(data)] <- 0
      data[base::is.null(data)] <- 0

      if (booled == "TRUE") {
       data[data > 0] <- 1
      }

      if (method == "cosine") {
        return(stats::as.dist(1 - coop::tcosine(data)))
      }else{
        return(stats::dist(data, method = method))
      }
    }
  ''')
  
except:
  print('did not load R')
  pass


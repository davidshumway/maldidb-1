from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import CommentForm
from .forms import SpectraForm
from .forms import MetadataForm
from .forms import LoadSqliteForm
from .forms import XmlForm
from .forms import LocaleForm
from .forms import VersionForm
from .forms import AddLibraryForm
from .forms import AddLabGroupForm
from .forms import LabProfileForm

from .models import Spectra
from .models import Metadata
from .models import XML
from .models import Locale
from .models import Version
from .models import Library
from .models import LabGroup

from django.db.models import Q
from django.views.generic import TemplateView, ListView

from .tables import LibraryTable, SpectraTable, MetadataTable, LabgroupTable

import django_filters
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import SingleTableView
import django_tables2 as tables


def library_profile(request, library_id):
  """View library"""
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

class LibrariesListView(SingleTableView):
  model = Library
  table_class = LibraryTable
  template_name = 'chat/libraries.html'

class SpectraFilter(django_filters.FilterSet):
  class Meta:
    model = Spectra
    exclude = ('id','picture') #fields = ['name', 'price', 'manufacturer']
    
# ~ def spectra_list(request):
  # ~ filter = SpectraFilter(request.GET, queryset=Spectra.objects.all())
  # ~ return render(request, 'chat/search_results.html', {'filter': filter})
  
# ~ class FilteredSpectraListView(SingleTableMixin, FilterView):
  # ~ table_class = SpectraTable
  # ~ model = Spectra
  # ~ template_name = 'chat/spectra.html'
  # ~ template_name = 'chat/search_results.html'
  # ~ filterset_class = SpectraFilter
  
  
  
class FilteredSpectraListView(SingleTableMixin, FilterView):
  table_class = SpectraTable
  model = Spectra
  template_name = 'chat/search_results.html'
  filterset_class = SpectraFilter
  
  # ~ def get_queryset(self):
    # ~ filter = SpectraFilter(self.request.GET, queryset=Spectra.objects.all())
    #return render(self.request, 'chat/spectra.html', {'filter': filter})
    # ~ return render(self.request, 'chat/search_results.html', {'filter': filter})
    
  # ~ def get_queryset(self):
    # ~ filter = SpectraFilter(request.GET, queryset=Spectra.objects.all())
    # ~ return render(request, 'chat/spectra.html', {'filter': filter})
    # all spectra from a given strain_id
    # ~ strain_id = self.request.GET.get('strain_id')
    # ~ object_list = Spectra.objects.filter(
      # ~ strain_id__strain_id__exact = strain_id
    # ~ )
    
    ### All species
    #species_list = Metadata.objects.order_by().values('strain_id').distinct()
    
    # ~ return object_list


    
class SpectraListView(SingleTableView):
  model = Spectra
  table_class = SpectraTable
  template_name = 'chat/spectra.html'
  
  def get_queryset(self):
    filter = SpectraFilter(request.GET, queryset=Spectra.objects.all())
    return render(request, 'chat/spectra.html', {'filter': filter})
    
  # ~ def get_queryset(self):
    
    # ~ # all spectra from a given strain_id
    # ~ strain_id = self.request.GET.get('strain_id')
    # ~ object_list = Spectra.objects.filter(
      # ~ strain_id__strain_id__exact = strain_id
      # ~ ###Q(metadata__strain_id__exact = strain_id)
    # ~ )
    
    # ~ ### All species
    # ~ #species_list = Metadata.objects.order_by().values('strain_id').distinct()
    
    # ~ return object_list

class MetadataListView(SingleTableView):
  model = Metadata
  table_class = MetadataTable
  template_name = 'chat/metadata.html'

class LabgroupsListView(SingleTableView):
  model = LabGroup
  table_class = LabgroupTable
  template_name = 'chat/labgroups.html'

def handle_uploaded_file(f, tmpForm):
  '''
    Works alongside upload_sqlite_file.
    Spectra is inserted last as it depends on XML and Metadata tables.
    Requires json and sqlite3 libraries.
    '''
  import json
  import sqlite3
  
  with open('/tmp/test.db', 'wb+') as destination:
    for chunk in f.chunks():
      destination.write(chunk)
      
  connection = sqlite3.connect('/tmp/test.db')
  cursor = connection.cursor()
  
  # ~ p = tmpForm.cleaned_data['library'].title
  # ~ p1 = tmpForm.cleaned_data['user']
  # ~ p2 = tmpForm.cleaned_data['library'][0].title
  # ~ p3 = tmpForm.cleaned_data['user'][0]
  # ~ p1 = tmpForm.cleaned_data['user']
  #p = tmpForm.cleaned_data['user'].filter(username=user) #objects.first()
  # ~ p1 = tmpForm.cleaned_data.get('library').value()
  
  
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
    }
    form = MetadataForm(data)
    if form.is_valid():
      entry = form.save(commit=False)
      entry.save()
    else:
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
    
    #print(row[2] + '--2')
    #print(row[3] + '--3')
    print(tmpForm.cleaned_data)
    print(tmpForm.cleaned_data['privacy_level'])
    print(tmpForm.cleaned_data['privacy_level'][0])
    
    smd = Metadata.objects.get(strain_id=row[3])
    sxml = XML.objects.get(xml_hash=row[2])
    
    pm = json.loads(row[4])
    
    data = {
      #'user': 2,
      #'user':     tmpForm.cleaned_data['user'][0].id,#.User, #tmpForm['user'],
      'created_by':     tmpForm.cleaned_data['user'][0].id,
      'library':  tmpForm.cleaned_data['library'][0].id,
      'lab_name':  tmpForm.cleaned_data['lab_name'][0].id,
      
      'privacy_level': tmpForm.cleaned_data['privacy_level'][0],
      
      'spectrum_mass_hash': row[0],
      'spectrum_intensity_hash': row[1],
      
      'xml_hash': smd.id,
      'strain_id': sxml.id,
      
      'peak_mass': ",".join(map(str, pm['mass'])),
      'peak_intensity': ",".join(map(str, pm['intensity'])),
      'peak_snr': ",".join(map(str, pm['snr'])),
      
      #'TESTxml_hash': row[2],
      #'TESTstrain_id': row[3],
      # ~ 'xml_hash': row[2],
      # ~ 'strain_id': row[3],
      
      
      # ~ 'peak_matrix': '', #TEMP row[4],
      # ~ 'spectrum_intensity': '',#TEMP row[5],
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
  users = list(request.user.followers.all())
  users.append(request.user)

  # Get posts from users accounts whose posts to display and order by latest
  #posts = Post.objects.filter(user__in=users).order_by('-posted_date')
  comment_form = CommentForm()
  
  # get xml
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


@login_required
def add_lib(request):
  if request.method == 'POST':
    form = AddLibraryForm(request.POST, request.FILES)
    if form.is_valid():
      entry = form.save(commit=False)
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
      handle_uploaded_file(request.FILES['file'], form)
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



# TESTING R
try:
  from rpy2.robjects import r as R

  print('loaded R')
  
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
  print("R['f'](3):", R['f'](3))
  print("R['f'](3) vvv:", R['f'](3, True))
  
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
  
except:
  print('did not load R')
  pass




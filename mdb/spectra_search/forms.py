from django import forms
from chat.models import *
from spectra.models import *
from files.models import UserFile
from dal import autocomplete
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.crypto import get_random_string # random library
User = get_user_model()

class SpectraCollectionsForm(forms.ModelForm):
  '''
    metadata [kingdom, ..., species], strain_id
    [lab, library]
  '''
  cKingdom = forms.ModelMultipleChoiceField(
    queryset = Metadata.objects.all(),
    label = 'Kingdom',
    widget = autocomplete.ModelSelect2Multiple(
	    url = 'spectra_search:metadata_autocomplete_kingdom')) # attrs = {'class': 'form-check-input'}
  cPhylum = forms.ModelMultipleChoiceField(
    queryset = Metadata.objects.all(),
    label = 'Phylum',
    widget = autocomplete.ModelSelect2Multiple(
      url = 'spectra_search:metadata_autocomplete_phylum', forward=('cKingdom',))
  )
  cClass = forms.ModelMultipleChoiceField(
    queryset = Metadata.objects.all(),
    label = 'Class',
    widget = autocomplete.ModelSelect2Multiple(
      url = 'spectra_search:metadata_autocomplete_class', forward=['cKingdom','cPhylum'])
  )
  cOrder = forms.ModelMultipleChoiceField(
    queryset = Metadata.objects.all(),
    label = 'Order',
    widget = autocomplete.ModelSelect2Multiple(
      url = 'spectra_search:metadata_autocomplete_order', forward=['cKingdom','cPhylum','cClass'])
  )
  cGenus = forms.ModelMultipleChoiceField(
    queryset = Metadata.objects.all(),
    label = 'Genus',
    widget = autocomplete.ModelSelect2Multiple(
      url = 'spectra_search:metadata_autocomplete_genus', forward=['cKingdom','cPhylum','cClass','cOrder'])
  )
  cSpecies = forms.ModelMultipleChoiceField(
    queryset = Metadata.objects.all(),
    label = 'Species',
    widget = autocomplete.ModelSelect2Multiple(
      url = 'spectra_search:metadata_autocomplete_species', forward=['cKingdom','cPhylum','cClass','cOrder','cGenus'])
  )
  
  class Meta:
    model = Metadata
    fields = ['cKingdom', 'cPhylum', 'cClass', 'cOrder', 'cGenus', 'cSpecies']
    # ~ widgets = {
      # ~ 'cGenus': autocomplete.ModelSelect2(url = 'chat:metadata_autocomplete'),
      # ~ 'cClass': autocomplete.Select2(url = 'chat:metadata_autocomplete'),
      # ~ 'cGenus': autocomplete.ModelSelect2(url = 'chat:metadata_autocomplete'),
      # ~ 'cClass': autocomplete.ModelSelect2(url = 'chat:metadata_autocomplete'),
    # ~ }

class LibraryModelChoiceField(forms.ModelChoiceField):
  def label_from_instance(self, obj):
    return f'{obj.title} | {obj.lab}'

class FileLibraryForm(forms.Form):
  '''
  Processes the library portion of an upload form.
  
  File is just a placeholder, i.e. no files uploaded via this form.
  ---whereas number_files represents the number of files in the File
  ---field.
  '''
  file = forms.FileField(
    label = 'Upload one or more files',
    required = False,
    widget = forms.ClearableFileInput(attrs={'multiple': True})
  )
  # ~ number_files = forms.IntegerField(widget = forms.HiddenInput(),
    # ~ initial = 0)
  
  search_from_existing = LibraryModelChoiceField(
    queryset = Library.objects.all(),
    # ~ to_field_name = 'id',
    required = False,
    widget = forms.Select(
      attrs = {
        'class': 'custom-select'}
    ),
    empty_label = 'Choose...'
  )
  
  # save to existing library
  library_select = forms.ModelChoiceField(
    queryset = Library.objects.all(),#.none(),
    to_field_name = 'title',
    required = False,
    widget = forms.Select(
      attrs = {
        'class': 'custom-select'}
    ),
    empty_label = 'Choose...'
  )
  
  library_create_new = forms.CharField(
    required = False,
    help_text = 'Enter a name for the new library',
    widget = forms.TextInput(
      attrs = {
        'class': 'form-control', 'placeholder': 'Enter a library title ...'}
    )
  )
  library_save_type = forms.CharField(label = '',
    widget = forms.RadioSelect(choices = [
      ('RANDOM', 'Random'),
      ('NEW', 'New'),
      ('EXISTING', 'Existing'),
    ])
  )
  
  # ~ use_filenames = forms.BooleanField(
    # ~ required = False,
    # ~ initial = True,
    # ~ label = 'Use filenames for strain IDs?')
  
  # ~ file_strain_ids = forms.CharField(
    # ~ required = False,
    # ~ widget = forms.Textarea(attrs = {'rows': 6, 'style': 'width:100%;'}),
    # ~ )
  
  preprocess = forms.BooleanField(
    required = True,
    initial = True,
    label = 'Perform spectra preprocessing?',
    disabled = True)
  
  def __init__(self, *args, **kwargs):
    request = kwargs.pop('request')
    self.user = request.user
    super(FileLibraryForm, self).__init__(*args, **kwargs)
    
  # ~ def clean_file_strain_ids(self):
    # ~ d = self.cleaned_data['file_strain_ids']
    # ~ if self.cleaned_data['use_filenames'] is False:
      # ~ try:
        # ~ if self.cleaned_data['number_files'] is False:
          # ~ raise forms.ValidationError('Field "number_files" missing!')
      # ~ except:
        # ~ raise forms.ValidationError('Field "number_files" missing!')
      # ~ if d.strip() == '':
        # ~ raise forms.ValidationError(
          # ~ 'List of filenames must not be empty!'
        # ~ )
      # ~ import re
      # ~ x = re.sub('[\r\n]+', '\n', d.strip())
      # ~ x = x.split('\n')
      # ~ # Entries == form entries
      # ~ if len(x) != self.cleaned_data['number_files']:
        # ~ raise forms.ValidationError(
          # ~ 'Number of filenames ({}) does not match number of files ({})!'
          # ~ .format(len(x), self.cleaned_data['number_files']))
      # ~ # < 255
      # ~ for tmpmd in x:
        # ~ if len(tmpmd.strip()) > 255:
          # ~ raise forms.ValidationError(
            # ~ 'Filenames contains an entry > 255 characters!')
      # ~ # Unique, e.g. [1,1] != {1}
      # ~ if len(set(x)) != len(x):
        # ~ raise forms.ValidationError(
            # ~ 'Filenames are not unique!')
    # ~ return d
  
  def clean(self):
    '''
    Adds "library" key
    '''
    d = super().clean()
    # ~ print(f'clean{d}')
    
    # validates upload library
    if d.get('library_save_type') == 'RANDOM':
      # user's uploads lab
      user_lab, created = LabGroup.objects.get_or_create(
        lab_name = self.user.username + '\'s uploads',
        lab_type = 'user-uploads',
        # ~ user_default_lab = True,
        owners__in = [self.user])
      if created:
        user_lab.owners.add(self.user)
        user_lab.members.add(self.user)
        user_lab.save()
      title = get_random_string(8)
      # Checks random entry doesn't exist
      x = False
      c = 100
      while x is False and c > 0:
        c -= 1
        n = Library.objects.filter(
          created_by = self.user,
          title = title,
          lab = user_lab
        )
        if len(n) == 0:
          x = True
          new_lib = Library.objects.create(
            created_by = self.user,
            title = title,
            lab = user_lab,
            privacy_level = 'PR'
          )
          d['library'] = new_lib
    elif d.get('library_save_type') == 'NEW':
      # user's library lab
      user_lab, created = LabGroup.objects.get_or_create(
        lab_name = self.user.username + '\'s default lab',
        lab_type = 'user-default',
        owners__in = [self.user])
      if created:
        user_lab.owners.add(self.user)
        user_lab.members.add(self.user)
        user_lab.save()
      n = Library.objects.filter(
        created_by = self.user,
        title = d.get('library_create_new'),
        lab = user_lab
      )
      if len(n) != 0:
        raise forms.ValidationError(
          'Library already exists!'
        )
      else:
        new_lib = Library.objects.create(
          created_by = self.user,
          title = d.get('library_create_new'),
          lab = user_lab,
          privacy_level = 'PR'
        )
        d['library'] = new_lib
    elif d.get('library_save_type') == 'EXISTING':
      d['library'] = d['library_select']
    
    return d
    
class SpectraLibraryForm(FileLibraryForm):
  '''
  Inherits FileLibraryForm and adds search logic.
  '''
  search_library = forms.ModelChoiceField(
    queryset = Library.objects.all(),
    # ~ to_field_name = 'title',
    required = False,
    widget = forms.Select(
      attrs = {
        'class': 'custom-select'}
    ),
    disabled = False,
    # ~ empty_label = 'Select a library to search against'
  )
  search_library_own = forms.ModelChoiceField(
    queryset = Library.objects.all(),
    # ~ to_field_name = 'title',
    required = False,
    widget = forms.Select(
      attrs = {
        'class': 'custom-select'}
    ),
    # ~ empty_label = 'Own library'
  )
  search_library_lab = forms.ModelChoiceField( # where user is a member or owner
    queryset = Library.objects.all(),
    # ~ to_field_name = 'title',
    required = False,
    widget = forms.Select(
      attrs = {
        'class': 'custom-select'}
    ),
    # ~ empty_label = 'Lab library'
  )
  search_library_public = forms.ModelChoiceField(
    queryset = Library.objects.all(),
    # ~ to_field_name = 'title',
    required = False,
    widget = forms.Select(
      attrs = {
        'class': 'custom-select'}
    ),
    # ~ empty_label = 'Public library'
  )
  library_search_type = forms.CharField(label = '',
    required = False,
    widget = forms.RadioSelect(choices = [
      ('r01', 'R01 datasets'),
      ('own', 'Own datasets'),
      ('lab', 'Lab datasets'),
      ('pub', 'Public datasets'),
    ])
  )
  
  cKingdom = forms.ModelMultipleChoiceField(
    queryset = Metadata.objects.all(),
    label = 'Kingdom', required = False,
    widget = autocomplete.ModelSelect2Multiple(
	    url = 'spectra_search:metadata_autocomplete_kingdom')) # attrs = {'class': 'form-check-input'}
  cPhylum = forms.ModelMultipleChoiceField(
    queryset = Metadata.objects.all(),
    label = 'Phylum', required = False,
    widget = autocomplete.ModelSelect2Multiple(
      url = 'spectra_search:metadata_autocomplete_phylum',
      forward=('cKingdom',)))
  cClass = forms.ModelMultipleChoiceField(
    queryset = Metadata.objects.all(),
    label = 'Class', required = False,
    widget = autocomplete.ModelSelect2Multiple(
      url = 'spectra_search:metadata_autocomplete_class',
      forward=['cKingdom','cPhylum']))
  cOrder = forms.ModelMultipleChoiceField(
    queryset = Metadata.objects.all(),
    label = 'Order', required = False,
    widget = autocomplete.ModelSelect2Multiple(
      url = 'spectra_search:metadata_autocomplete_order',
      forward=['cKingdom','cPhylum','cClass']))
  cGenus = forms.ModelMultipleChoiceField(
    queryset = Metadata.objects.all(),
    label = 'Genus', required = False,
    widget = autocomplete.ModelSelect2Multiple(
      url = 'spectra_search:metadata_autocomplete_genus',
      forward=['cKingdom','cPhylum','cClass','cOrder']))
  cSpecies = forms.ModelMultipleChoiceField(
    queryset = Metadata.objects.all(),
    label = 'Species', required = False,
    widget = autocomplete.ModelSelect2Multiple(
      url = 'spectra_search:metadata_autocomplete_species',
      forward=['cKingdom','cPhylum','cClass','cOrder','cGenus']))
  
  def clean(self):
    '''
    
    '''
    d = super().clean()
    # ~ print(f'clean{d}')
    
    # validates search library
    if d.get('library_search_type') == 'r01':
      pass
    elif d.get('library_search_type') == 'own':
      d['search_library'] = d['search_library_own']
    elif d.get('library_search_type') == 'lab':
      d['search_library'] = d['search_library_lab']
    elif d.get('library_search_type') == 'pub':
      d['search_library'] = d['search_library_public']
    
    return d
  
class MetadataUploadForm(forms.ModelForm):
  file = forms.FileField(
    label = 'Upload one or more files',
    required = True,
    widget = forms.ClearableFileInput(attrs={'multiple': True})
  )
  upload_count = forms.IntegerField(required = True)
  library_id = forms.IntegerField(required = True)
  client = forms.CharField(required = True)
  
  class Meta:
    model = UserFile
    exclude = ('id', 'owner', 'upload_date', 'extension')
    widgets = {
      'lab': forms.Select(
        attrs = {'class': 'custom-select'}
      ),
    }
  
  def save(self, commit = True):
    instance = super().save(commit=False)
    if self.request.user.is_authenticated:
      instance.owner = self.request.user
    instance.extension = 'csv'
    instance.save(commit)
    return instance
  
  def __init__(self, *args, **kwargs):
    request = kwargs.pop('request')
    self.user = request.user
    super(MetadataUploadForm, self).__init__(*args, **kwargs)
    user = self.user
    
class SpectraUploadForm(forms.ModelForm):
  file = forms.FileField(
    label = 'Upload one or more files',
    required = True,
    widget = forms.ClearableFileInput(attrs={'multiple': True})
  )
  upload_count = forms.IntegerField(require = True)
  library_id = forms.IntegerField(required = True)
  client = forms.CharField(required = True)
  
  class Meta:
    model = UserFile
    exclude = ('id', 'owner', 'upload_date', 'extension')
    widgets = {
      'lab': forms.Select(
        attrs = {'class': 'custom-select'}
      ),
    }
  
  def save(self, commit = True):
    instance = super().save(commit=False)
    if self.request.user.is_authenticated:
      instance.owner = self.request.user
    instance.save(commit)
    return instance
  
  def __init__(self, *args, **kwargs):
    request = kwargs.pop('request')
    self.user = request.user
    super(SpectraUploadForm, self).__init__(*args, **kwargs)
    user = self.user
  
  # ~ def clean(self):
    # ~ d = super().clean()
    # ~ try:
      # ~ d['library_id'] = Library.objects.get(id = d['library_id'])
    # ~ except:
      # ~ raise forms.ValidationError('Missing library!')
    # ~ return d
          
class SpectraSearchForm(forms.ModelForm):
  '''Replicated, Collapsed, all
  Small molecule, Protein, all [or range, e.g., 3k-8k]
  Processed spectra, raw spectra (run pipeline?)
  '''
  
  choices = [
    ('collapsed', 'Collapsed Spectra'),
    ('replicate', 'Replicates'),
    ('all', 'All'),
  ]
  replicates = forms.ChoiceField(
    label = 'Spectrum type',
    widget = forms.RadioSelect(choices = choices),
    choices = choices,
    required = True,
    initial = 'collapsed')
  
  choices = [
    ('protein', 'Protein'),
    ('small', 'Small Molecule'),
    ('all', 'All'),
  ]
  spectrum_cutoff = forms.ChoiceField(
    label = 'Spectrum cutoff', 
    widget = forms.RadioSelect,
    choices = choices,
    required = True,
    initial = 'protein')
  
  choices = [
    ('processed', 'Processed Spectrum'),
    ('raw', 'Raw Spectrum'),
  ]
  preprocessing = forms.ChoiceField(
    label = 'Spectrum state:',
    widget = forms.RadioSelect(choices = choices),
    choices = choices,
    initial = 'processed')
  
  labXX = forms.ModelMultipleChoiceField(
    queryset = LabGroup.objects.all(),
    to_field_name = "lab_name",
    required = False
  )
  libraryXX = forms.ModelMultipleChoiceField(
    queryset = Library.objects.all(),
    to_field_name = "title",
    required = False
  )
  strain_idXX = forms.ModelMultipleChoiceField(
    queryset = Metadata.objects.order_by('strain_id').distinct('strain_id'),
    to_field_name = "strain_id",
    required = False
  )
  distinct_users = Spectra.objects.order_by('created_by') \
    .values_list('created_by',flat=True).distinct()
  created_byXX = forms.ModelMultipleChoiceField(
    queryset = User.objects.all().filter(id__in = distinct_users),
    to_field_name = "username", 
    required = False
  )
  xml_hashXX = forms.ModelMultipleChoiceField(
    queryset = XML.objects.order_by('xml_hash').distinct('xml_hash'),
    required = False
  )
  
  def clean(self):
    data = self.cleaned_data
    print('dpm',data.get('peak_mass'))
    s1 = (
      data.get('peak_mass') != '' or data.get('peak_intensity') != '' or data.get('peak_snr') != ''
    )
    s2 = (
      data.get('peak_mass') == '' or data.get('peak_intensity') == '' or data.get('peak_snr') == ''
    )
    if s1 and s2:
      raise forms.ValidationError(
        'Peak mass, intensity, and SNR must be entered!'
      )
    else:
      return data
    
  class Meta:
    '''
    -- jQuery tooltip utilizes data-toggle and title attrs
    -- Multiple select fields need to not be the model, because the model
       expects these to be a single ID, e.g., library, strain_id, lab_name.
    '''
    model = Spectra
    exclude = (
      'id', 'picture', 'description', 'library', 'strain_id', 'lab',
      'created_by', 'xml_hash'
    )
    widgets = {
      'peak_mass': forms.TextInput(
        attrs={'placeholder': '1,2,3', 'class': 'form-control',
          'data-toggle': 'tooltip',
          'title': 'A list of comma separated values, e.g., "1,2,3"'}
      ),
      'peak_intensity': forms.TextInput(
        attrs={'placeholder': '1,2,3', 'class': 'form-control',
          'data-toggle': 'tooltip',
          'title': 'A list of comma separated values, e.g., "1,2,3"'}
      ),
      'peak_snr': forms.TextInput(
        attrs={'placeholder': '1,2,3', 'class': 'form-control',
          'data-toggle': 'tooltip',
          'title': 'A list of comma separated values, e.g., "1,2,3"'}
      ),
      'spectrum_cutoff_low': forms.TextInput(
        attrs={'size': 6, 'placeholder': 'Min. M/Z', 'class': 'form-control'}
      ),
      'spectrum_cutoff_high': forms.TextInput(
        attrs={'size': 6, 'placeholder': 'Max. M/Z', 'class': 'form-control'}
      ),
      'calibration_constants': forms.Textarea(
        attrs={'rows': 1, 'cols': 10, 'placeholder': ''}
      ),
      'v1_tof_calibration': forms.Textarea(
        attrs={'rows': 1, 'cols': 10, 'placeholder': ''}
      ),
    }

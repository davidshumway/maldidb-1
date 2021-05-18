from django import forms
from chat.models import *
from spectra.models import *
from files.models import UserFile
from dal import autocomplete
from django.contrib.auth import get_user_model
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
  # ~ lab_name = forms.ModelChoiceField(
    # ~ queryset = LabGroup.objects.all(),
    # ~ to_field_name = "lab_name",
    # ~ required = False,
    # ~ widget = forms.Select(
      # ~ attrs = {
        # ~ 'class': 'custom-select'}
    # ~ ),
    # ~ disabled = True,
    # ~ empty_label='Select a lab'
  # ~ )
  # ~ library = forms.ModelChoiceField(
    # ~ queryset = Library.objects.all(),
    # ~ to_field_name = "title",
    # ~ required = False,
    # ~ widget = forms.Select(
      # ~ attrs = {
        # ~ 'class': 'custom-select'}
    # ~ ),
    # ~ disabled = True,
    # ~ empty_label='Select a library'
  # ~ )
  
# ~ class SpectraUploadForm(forms.ModelForm):
  # ~ pass
  # ~ class Meta:
    # ~ model = UserFile
    # ~ exclude = ('id', 'owner', 'upload_date', 'extension')
    # ~ #custom-select
    # ~ widgets = {
      # ~ 'lab_name': forms.Select(
        # ~ attrs = {
          # ~ 'class': 'custom-select'}
      # ~ ),
    # ~ }

class SpectraUploadForm(forms.ModelForm):
  file = forms.FileField(
    label = 'Upload a file',
    required = True
  )
  
  # Options
  
  # Save spectra to lab->library?
  # otherwise, save to user's (temporary spectra) library
  save_to_library = forms.BooleanField(
    required = False,
    label = 'Save upload to preexisting library? (optional)',
    widget = forms.CheckboxInput(
      attrs = {
        'class': 'form-check-input'}
    )
  )
  # If yes... todo: filter by user's membership and/or public libs
  lab = forms.ModelChoiceField(
    queryset = LabGroup.objects.all(),
    to_field_name = "lab_name",
    required = False,
    widget = forms.Select(
      attrs = {
        'class': 'custom-select'}
    ),
    disabled = True,
    empty_label = 'Select a lab'
  )
  library = forms.ModelChoiceField(
    queryset = Library.objects.all(),
    to_field_name = "title",
    required = False,
    widget = forms.Select(
      attrs = {
        'class': 'custom-select'}
    ),
    disabled = True,
    empty_label = 'Select a library'
  )
  forms.MultipleChoiceField(choices = [
      ('PB', 'Public'),
      ('PR', 'Private'),
    ],
    initial = 'PR'
  )
  # ~ privacy_level = forms.ChoiceField(
    # ~ choices = [
      # ~ ('PUBLIC', 'Public'),
      # ~ ('PRIVATE', 'Private')
    # ~ ],
    # ~ required = True,
    # ~ initial = 'PRIVATE',
    # ~ label = 'Privacy:')
    
  preprocess = forms.BooleanField(
    required = True,
    initial = True,
    label = 'Perform spectra preprocessing?')
  
  class Meta:
    model = UserFile
    exclude = ('id', 'owner', 'upload_date', 'extension')
    #custom-select
    widgets = {
      'lab': forms.Select(
        attrs = {
          'class': 'custom-select'}
      ),
    }
  
  def save(self, commit = True):
    instance = super().save(commit=False)
    if self.request.user.is_authenticated:
      instance.owner = self.request.user
    instance.save(commit)
    return instance
    
  def clean(self):
    '''
    -- If saving, then lab/library must be present and valid selection
    '''
    data = self.cleaned_data
    s1 = (
      data.get('save_to_library') == True and (data.get('lab') == '' or data.get('library') == '')
    )
    #  ll_err = False
    #  if data.get('save_to_library') == True:
      #  try:
        #  LabGroup.objects.get(data.get('lab_name'))
      #  except:
        #  ll_err = forms.ValidationError(
          #  'Lab group not found!'
        #  )
      #  try:
        #  Library.objects.get(data.get('library'))
      #  except:# Library.DoesNotExist:
        #  ll_err = forms.ValidationError(
          #  'Library not found!'
        #  )
    if s1:
      raise forms.ValidationError(
        'Lab group and library must be specified if "Save to Library" is selected'
      )
    #  elif ll_err:
      #  raise ll_err
    else:
      return data
      
class SpectraSearchForm(forms.ModelForm):
  '''Replicated, Collapsed, all
  Small molecule, Protein, all [or range, e.g., 3k-8k]
  Processed spectra, raw spectra (run pipeline?)'''
  
  # ~ prefix = 'fm'
  
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
    # ~ ('custom', 'Custom'),
  ]
  spectrum_cutoff = forms.ChoiceField(
    label = 'Spectrum cutoff', 
    widget = forms.RadioSelect,
    choices = choices,
    required = True,
    initial = 'protein')
  # on custom, then allow for a range
  # ~ spectrum_cutoff_low = forms.IntegerField(
    # ~ label = 'Minimum M/Z',
    # ~ min_value = 0, disabled = True,
    # ~ required = False)
  # ~ spectrum_cutoff_high = forms.IntegerField(
    # ~ label = 'Maximum M/Z',
    # ~ min_value = 0, disabled = True,
    # ~ required = False)
  
  choices = [
    ('processed', 'Processed Spectrum'),
    ('raw', 'Raw Spectrum'),
  ]
  preprocessing = forms.ChoiceField(
    label = 'Spectrum state:',
    widget = forms.RadioSelect(choices = choices),
    choices = choices,
    initial = 'processed')
  # on raw, include preprocessing options
  # (todo?)
  
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
  
  # ~ def __init__(self, *args, **kwargs):
    # ~ print(f'_init_-args: {args}') # 
    # ~ print(f'_init_-kw:   {kwargs}') # 
    # ~ super(SpectraSearchForm, self).__init__(*args, **kwargs)
  
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
      # ~ 'library': forms.SelectMultiple(),
    }

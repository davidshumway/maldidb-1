from django import forms

from .models import Comment, Spectra, Metadata, XML, Locale, Version, \
  Library, PrivacyLevel, LabGroup, SpectraCosineScore, XML, UserFile

from dal import autocomplete

from django.contrib.auth import get_user_model
User = get_user_model()


class LibraryCollapseForm(forms.Form):
  '''
  Select: Collapse all replicates marked as "Linear" vs. "Reflector"
  User selects a library.
  Spectra are grouped by machine setting linear vs. reflector.
  Spectra then grouped by strain id.
  '''
  # ~ library = forms.CharField(disabled = True, required = True)
  library = forms.ModelChoiceField(
    queryset = Library.objects.all(),
    # ~ to_field_name = "title",
    required = False 
  )
  
  #CollapsedSpectra
  peak_percent_presence = forms.DecimalField( # e.g. 70.00%
    max_value=100, decimal_places=1, initial=70.0)
  #lower_mass_cutoff = models.IntegerField(blank=True) #e.g. 0
  #upper_mass_cutoff = models.IntegerField(blank=True) #e.g. 6000
  min_snr = forms.DecimalField(
    decimal_places=2, initial=0.25) #e.g.?
  tolerance = forms.DecimalField(
    decimal_places=3, initial=0.002)
  
  spectraChoices = [
    ('protein', 'Protein'),
    ('sm', 'Small Molecule'),
    ('all', 'All'),
  ]
  collapse_types = forms.ChoiceField(
    label = 'Select replicates to collapse',
    choices = spectraChoices,
    widget = forms.RadioSelect,
    initial = 'all',
    required = True
  )
  
  #generated_date = forms.DateTimeField(auto_now_add=True, blank=True)
  
  class Meta:
    model = Library
    fields = ['id']
    
  # ~ def __init__(self, *args, **kwargs):
    # ~ g = kwargs.pop('get','')
    
    # Get initial data passed from the view
    #self.library = None
    #if 'library' in kwargs['initial']:
    #  self.library = kwargs['initial'].pop('library')
    
    # ~ super(LibraryCollapseForm, self).__init__(*args, **kwargs)
      
    #self.fields['library'].queryset = Library.objects.filter(id=self.library)
    # ~ print(f'_init_-args: {args}')
    # ~ print(f'_init_-args: {kwargs}')
    #if 
    # ~ self.fields['metadata_strain_ids'] = forms.ModelChoiceField(queryset=Metadata.objects.all())
    
class SpectraCollectionsForm(forms.ModelForm):
  '''
    metadata [kingdom, ..., species], strain_id
    [lab, library]
  '''
  cKingdom = forms.ModelMultipleChoiceField(
    queryset = Metadata.objects.all(),
    label = 'Kingdom',
    widget = autocomplete.ModelSelect2Multiple(url = 'chat:metadata_autocomplete_kingdom')) # attrs = {'class': 'form-check-input'}
  cPhylum = forms.ModelMultipleChoiceField(
    queryset = Metadata.objects.all(),
    label = 'Phylum',
    widget = autocomplete.ModelSelect2Multiple(url = 'chat:metadata_autocomplete_phylum', forward=('cKingdom',))
  )
  cClass = forms.ModelMultipleChoiceField(
    queryset = Metadata.objects.all(),
    label = 'Class',
    widget = autocomplete.ModelSelect2Multiple(url = 'chat:metadata_autocomplete_class', forward=['cKingdom','cPhylum'])
  )
  cOrder = forms.ModelMultipleChoiceField(
    queryset = Metadata.objects.all(),
    label = 'Order',
    widget = autocomplete.ModelSelect2Multiple(url = 'chat:metadata_autocomplete_order', forward=['cKingdom','cPhylum','cClass'])
  )
  cGenus = forms.ModelMultipleChoiceField(
    queryset = Metadata.objects.all(),
    label = 'Genus',
    widget = autocomplete.ModelSelect2Multiple(url = 'chat:metadata_autocomplete_genus', forward=['cKingdom','cPhylum','cClass','cOrder'])
  )
  cSpecies = forms.ModelMultipleChoiceField(
    queryset = Metadata.objects.all(),
    label = 'Species',
    widget = autocomplete.ModelSelect2Multiple(url = 'chat:metadata_autocomplete_species', forward=['cKingdom','cPhylum','cClass','cOrder','cGenus'])
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
  lab_name = forms.ModelChoiceField(
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
  
  # perform (default) preprocessing?
  preprocess = forms.BooleanField(
    required = False,
    initial = True,
    label = 'Perform spectra preprocessing? (optional)')
  
  class Meta:
    model = UserFile
    exclude = ('id', 'owner', 'upload_date', 'extension')
    #custom-select
    widgets = {
      'lab_name': forms.Select(
        attrs = {
          'class': 'custom-select'}
      ),
    }
  
  def save(self, commit = True):
    instance = super().save(commit=False)
    instance.owner = self.request.user
    instance.save(commit)
    # ~ print('userfile instance',instance)
    return instance
    
  def clean(self):
    '''
    -- If saving, then lab/library must be present and valid selection
    '''
    data = self.cleaned_data
    s1 = (
      data.get('save_to_library') == True and (data.get('lab_name') == '' or data.get('library') == '')
    )
    # ~ ll_err = False
    # ~ if data.get('save_to_library') == True:
      # ~ try:
        # ~ LabGroup.objects.get(data.get('lab_name'))
      # ~ except:
        # ~ ll_err = forms.ValidationError(
          # ~ 'Lab group not found!'
        # ~ )
      # ~ try:
        # ~ Library.objects.get(data.get('library'))
      # ~ except:# Library.DoesNotExist:
        # ~ ll_err = forms.ValidationError(
          # ~ 'Library not found!'
        # ~ )
    if s1:
      raise forms.ValidationError(
        'Lab group and library must be specified if "Save to Library" is selected!'
      )
    # ~ elif ll_err:
      # ~ raise ll_err
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
  
  lab_nameXX = forms.ModelMultipleChoiceField(
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
  distinct_users = Spectra.objects.order_by('created_by').values_list('created_by',flat=True).distinct()
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
      'id','picture','description','library','strain_id','lab_name',
      'created_by','xml_hash'
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
    
class ViewCosineForm(forms.Form):
  '''
  Select any spectra from lab, library, metadata
  '''
  lab_name = forms.ModelMultipleChoiceField(
    queryset = LabGroup.objects.all(),
    to_field_name = "lab_name",
    required = False
  )
  library = forms.ModelMultipleChoiceField(
    queryset = Library.objects.all(),
    to_field_name = "title",
    required = False
  )
  
  #class Meta:
    #model = SpectraCosineScore
  #  exclude = ('id',) 

class SpectraEditForm(forms.ModelForm):
  class Meta:
    model = Spectra
    exclude = ('id','created_by',) 

class LibProfileForm(forms.ModelForm):
  class Meta:
    model = Library
    exclude = ('id',) 

class LabProfileForm(forms.ModelForm):
  class Meta:
    model = LabGroup
    exclude = ('id',) 

class SearchForm(forms.ModelForm):
  """Search by peaks/intensities, or upload mzXML or mzML file."""
  #strain_id = forms.ModelChoiceField(queryset=Metadata.objects.all())
  # ~ strain_id = Metadata.strain_id
  class Meta:
    model = Spectra
    exclude = ('id',)

  def __init__(self, *args, **kwargs):
    #user = kwargs.pop('user','')
    #super(DocumentForm, self).__init__(*args, **kwargs)
    self.fields['metadata_strain_ids'] = forms.ModelChoiceField(queryset=Metadata.objects.all())

  
class AddXmlForm(forms.ModelForm):
  class Meta:
    model = XML
    exclude = ('created_by',)
  
class AddLabGroupForm(forms.ModelForm):
  class Meta:
    model = LabGroup
    exclude = ('created_by',)

class AddLibraryForm(forms.ModelForm):
  class Meta:
    model = Library
    exclude = ('created_by',)
  
class LoadSqliteForm(forms.Form):
  # ~ user = forms.ModelMultipleChoiceField(
    # ~ queryset = user.objects.all(), to_field_name="username"
  # ~ )
  lab_name = forms.ModelChoiceField(
    queryset = LabGroup.objects.all(), to_field_name="lab_name"
  )
  library = forms.ModelChoiceField(
    queryset = Library.objects.all(), to_field_name="title"
  )
  
  choices = [
    ('single', 'Load a single IDBac SQLite file'),
    ('all', 'Load all IDBac R01 data files'),
  ]
  upload_type = forms.CharField(
    label = 'Upload type',
    widget = forms.RadioSelect(choices = choices),
    required = True,
    initial = 'single')
    
  file = forms.FileField(required = False,
    label = 'Select an IDBac SQLite file to upload')
  
  PUBLIC = 'PB'
  PRIVATE = 'PR'
  privacyChoices = [
    (PUBLIC, 'Public'),
    (PRIVATE, 'Private'),
  ]
  privacy_level = forms.MultipleChoiceField(choices = privacyChoices)
  # ~ privacy_level = forms.ModelMultipleChoiceField(
    # ~ queryset = PrivacyLevel.objects.all(), to_field_name="username"
     # ~ #User.objects.all() # todo: add more description per entry
  # ~ )
  
  def clean(self):
    data = self.cleaned_data
    print('add form',data)
    # ~ raise forms.ValidationError(
      # ~ 'Select a file to upload!'
    # ~ )
    if data.get('file') == None and data.get('upload_type') == 'single':
      raise forms.ValidationError(
        'Select a file to upload!'
      )
    else:
      return data
      


class MetadataModelChoiceField(forms.ModelChoiceField):
  def label_from_instance(self, obj):
    # ~ return "My Object #%i" % obj.id
    return obj.strain_id
    
class SpectraForm(forms.ModelForm):
  """
  Form for handling addition of spectra
  """
  
  #md = forms.ModelMultipleChoiceField(
  #  queryset = Metadata.objects.all() # todo: add more description per entry
  #)
  
  # ~ library = forms.ModelMultipleChoiceField(
    # ~ queryset = Library.objects.all()
  # ~ )
  # ~ user = forms.ModelMultipleChoiceField(
    # ~ queryset = user.objects.all() #User.objects.all() # todo: add more description per entry
  # ~ )
  
  #def save(self, commit=True):
    # ~ instance = super().save(commit=False)
    # ~ lib = self.cleaned_data['library']
    # ~ instance.library = lib[0]
    # ~ usr = self.cleaned_data['user']
    # ~ instance.user = usr[0]
    # ~ instance.save(commit)
    # ~ return instance
  
  # overwrite strain_id to alter label from {Metadata-object} to
  # {Metadata-object}.strain_id 
  # ~ strain_id = MetadataModelChoiceField(
    # ~ queryset = Metadata.objects.all(),
    # ~ empty_label = None,
    # ~ required = False,
    # ~ to_field_name = 'strain_id',
    # ~ label = 'Strain ID',
    # ~ widget = forms.ModelMultipleChoiceField()
    # ~ #SelectMultiple
  # ~ )

  class Meta:
    model = Spectra
    exclude = ('id',)
    # ~ exclude = ('created_by',)
    widgets = {
      'description': forms.Textarea(
        attrs={'rows': 1, 'cols': 40, 'placeholder': 'General description of the spectra.'}
      ),
      'peak_mass': forms.Textarea(
        attrs={'rows': 1, 'cols': 40, 'placeholder': 'A comma-separated list, e.g., "110.1,112.2".'}
      ),
      'peak_intensity': forms.Textarea(
        attrs={'rows': 1, 'cols': 40, 'placeholder': 'A comma-separated list, e.g., "4.1,4.2".'}
      ),
      'peak_snr': forms.Textarea(
        attrs={'rows': 1, 'cols': 40, 'placeholder': 'A comma-separated list, e.g., "1.1,1.2".'}
      ),
      'calibration_constants': forms.Textarea(
        attrs={'rows': 1, 'cols': 40, 'placeholder': ''}
      ),
      'v1_tof_calibration': forms.Textarea(
        attrs={'rows': 1, 'cols': 40, 'placeholder': ''}
      ),
    }

class XmlForm(forms.ModelForm):
  class Meta:
    model = XML
    # ~ exclude = ('id','created_by','xml')
    exclude = ('id','xml',)
    # ~ fields = ('xml_hash','xml','manufacturer','model','ionization','analyzer','detector','instrument_metafile')
    
class MetadataForm(forms.ModelForm):
  """
  Form for handling addition of metadata
  """
                            
  class Meta:
    model = Metadata
    # ~ exclude = ('created_by',)
    exclude = ('id',)
    widgets = {
      'cKingdom': forms.Textarea(
        attrs={'rows': 1, 'cols': 40, 'placeholder': ''}
      ),
      'cPhylum': forms.Textarea(
        attrs={'rows': 1, 'cols': 40, 'placeholder': ''}
      ),
      'cClass': forms.Textarea(
        attrs={'rows': 1, 'cols': 40, 'placeholder': ''}
      ),
      'cOrder': forms.Textarea(
        attrs={'rows': 1, 'cols': 40, 'placeholder': ''}
      ),
      'cGenus': forms.Textarea(
        attrs={'rows': 1, 'cols': 40, 'placeholder': ''}
      ),
      'cSpecies': forms.Textarea(
        attrs={'rows': 1, 'cols': 40, 'placeholder': ''}
      ),
    }

class LocaleForm(forms.ModelForm):
  class Meta:
    model = Locale
    exclude = ()

class VersionForm(forms.ModelForm):
  class Meta:
    model = Version
    exclude = ()
    
class CommentForm(forms.Form):
  """
  Form for adding comments
  """

  text = forms.CharField(
    label="Comment",
    widget=forms.Textarea(attrs={'rows': 2})
  )

  def save(self, spectra, user):
    """
    custom save method to create comment
    """
    comment = Comment.objects.create(
      text=self.cleaned_data.get('text', None),
      post = spectra,
      user = user)

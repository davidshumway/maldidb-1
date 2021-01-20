from django import forms

from .models import Comment, Spectra, Metadata, XML, Locale, Version
from .models import Library, PrivacyLevel, LabGroup, SpectraCosineScore, XML

from django.contrib.auth import get_user_model
User = get_user_model()

class SpectraSearchForm(forms.ModelForm):
  '''Replicated, Collapsed, all
  Small molecule, Protein, all [or range, e.g., 3k-8k]
  Processed spectra, raw spectra (run pipeline?)'''
  
  # ~ prefix = 'fm'
  
  spectra_file = forms.FileField(
    label = 'Upload a spectrum file',
    required = False
  )
  
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
    ('custom', 'Custom'),
  ]
  spectrum_cutoff = forms.ChoiceField(
    label = 'Spectrum cutoff', 
    widget = forms.RadioSelect,
    choices = choices,
    required = True,
    initial = 'protein')
  # on custom, then allow for a range
  spectrum_cutoff_low = forms.IntegerField(
    label = 'Minimum M/Z',
    min_value = 0, disabled = True,
    required = False)
  spectrum_cutoff_high = forms.IntegerField(
    label = 'Maximum M/Z',
    min_value = 0, disabled = True,
    required = False)
  
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
    # ~ queryset = Spectra.objects.order_by('strain_id').distinct('strain_id'),
    queryset = Metadata.objects.order_by('strain_id').distinct('strain_id'),
    to_field_name = "strain_id",
    required = False
  )
  distinct_users = Spectra.objects.order_by('created_by').values_list('created_by',flat=True).distinct()
  created_byXX = forms.ModelMultipleChoiceField(
    queryset = User.objects.all().filter(id__in = distinct_users),
    # ~ queryset = Spectra.objects.order_by('created_by').distinct('created_by'),
    # ~ queryset = User.objects.all().filter(id__in = ),
    to_field_name = "username", 
    required = False
  )
  xml_hashXX = forms.ModelMultipleChoiceField(
    # ~ queryset = Spectra.objects.order_by('xml_hash').distinct('xml_hash'),
    queryset = XML.objects.order_by('xml_hash').distinct('xml_hash'),
    # ~ to_field_name = "xml_hash",
    required = False
  )
  
  # ~ def __init__(self, *args, **kwargs):
    # ~ print(f'_init_-args: {args}' ) # 
    # ~ print(f'_init_-kw:   {kwargs}' ) # 
    # ~ super(SpectraSearchForm, self).__init__(*args, **kwargs)
  
  def clean(self):
    data = self.cleaned_data
    # ~ print('add form',data)
    # ~ raise forms.ValidationError(
      # ~ 'Select a file to upload!'
    # ~ )
    # ~ if data.get('file') == None and data.get('upload_type') == 'single':
      # ~ raise forms.ValidationError(
        # ~ 'Select a file to upload!'
      # ~ )
    print('dpm',data.get('peak_mass'))
    if (data.get('peak_mass') != '' or data.get('peak_intensity') != '' or data.get('peak_snr') != '') and (data.get('peak_mass') == '' or data.get('peak_intensity') == '' or data.get('peak_snr') == ''):
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
    
class ViewCosineForm(forms.ModelForm):
  class Meta:
    model = SpectraCosineScore
    exclude = ('id',) 

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
  lab_name = forms.ModelMultipleChoiceField(
    queryset = LabGroup.objects.all(), to_field_name="lab_name"
  )
  library = forms.ModelMultipleChoiceField(
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
    
  file = forms.FileField(required = False, label = 'Select an IDBac SQLite file to upload')
  
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
    comment = Comment.objects.create(text=self.cleaned_data.get('text', None), post=spectra, user=user)

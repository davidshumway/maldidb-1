from django import forms

from .models import Comment, Spectra, Metadata, XML, Locale, Version
from .models import Library, PrivacyLevel, LabGroup, SpectraCosineScore, XML

from django.contrib.auth import get_user_model
user = get_user_model()

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
    ('replicate', 'Replicates'),
    ('collapsed', 'Collapsed Spectra'),
    ('all', 'All'),
  ]
  replicates = forms.CharField(
    label = 'Spectrum type',
    widget = forms.RadioSelect(choices = choices),
    required = True)
  
  choices = [
    ('small', 'Small Molecule'),
    ('protein', 'Protein'),
    ('all', 'All'),
    ('custom', 'Custom'),
  ]
  spectrum_cutoff = forms.CharField(
    label = 'Spectrum cutoff',
    widget = forms.RadioSelect(choices = choices),
    required = True)
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
  preprocessing = forms.CharField(
    label = 'Spectrum state:',
    widget = forms.RadioSelect(choices = choices))
  # on raw, include preprocessing options
  
  
  class Meta:
    '''
    jquery tooltip utilizes data-toggle and title attrs
    '''
    model = Spectra
    exclude = ('id','picture','description')
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
  
  file = forms.FileField()
  
  # multi select from all sqlite files (temporary), presently hosted
  hc = [
    ('2019_04_15_10745_db-2_0_0.sqlite','2019_04_15_10745_db-2_0_0.sqlite'),
    ('2019_07_02_22910_db-2_0_0.sqlite','2019_07_02_22910_db-2_0_0.sqlite'),
    ('2019_09_11_1003534_db-2_0_0.sqlite','2019_09_11_1003534_db-2_0_0.sqlite'),
    ('2019_10_10_1003534_db-2_0_0.sqlite','2019_10_10_1003534_db-2_0_0.sqlite'),
    ('2019_06_06_22910_db-2_0_0.sqlite','2019_06_06_22910_db-2_0_0.sqlite'),
    ('2019_06_06_22910_db-2_0_0.sqlite','2019_06_06_22910_db-2_0_0.sqlite'),
    ('2019_09_18_22910_db-2_0_0.sqlite','2019_09_18_22910_db-2_0_0.sqlite'),
    ('2019_11_13_1003534_db-2_0_0.sqlite','2019_11_13_1003534_db-2_0_0.sqlite'),
    ('2019_06_12_10745_db-2_0_0.sqlite','2019_06_12_10745_db-2_0_0.sqlite'),
    ('2019_09_04_10745_db-2_0_0.sqlite','2019_09_04_10745_db-2_0_0.sqlite'),
    ('2019_09_25_10745_db-2_0_0.sqlite','2019_09_25_10745_db-2_0_0.sqlite'),
    ('2019_11_20_1003534_db-2_0_0.sqlite','2019_11_20_1003534_db-2_0_0.sqlite')
  ]
  hosted_files__tmp = forms.MultipleChoiceField(choices = hc)
  
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
    #fields = ('peaks', 'intensities')
    exclude = ('created_by',)
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
    exclude = ('id','created_by','xml')
    # ~ fields = ('xml_hash','xml','manufacturer','model','ionization','analyzer','detector','instrument_metafile')
    
class MetadataForm(forms.ModelForm):
  """
  Form for handling addition of metadata
  """
                            
  class Meta:
    model = Metadata
    exclude = ('created_by',)
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

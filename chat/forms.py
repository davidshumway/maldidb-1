from django import forms

from .models import Comment, Spectra, Metadata, XML, Locale, Version
from .models import Library, PrivacyLevel, LabGroup, SpectraCosineScore

from django.contrib.auth import get_user_model
user = get_user_model()

class SpectraSearchForm(forms.ModelForm):
  '''Replicated, Collapsed, all
  Small molecule, Protein, all [or range, e.g., 3k-8k]
  Processed spectra, raw spectra (run pipeline?)'''
  
  prefix = 'spectra_search'
  
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
    model = Spectra
    exclude = ('id',)
    widgets = {
      'peak_mass': forms.TextInput(
        attrs={'size': 2, 'placeholder': '', 'class': 'form-control'}
      ),
      'peak_intensity': forms.TextInput(
        attrs={'size': 2, 'placeholder': '', 'class': 'form-control'}
      ),
      'peak_snr': forms.TextInput(
        attrs={'size': 2, 'placeholder': '', 'class': 'form-control'}
      ),
      'spectrum_cutoff_low': forms.TextInput(
        attrs={'size': 6, 'placeholder': 'Min. M/Z', 'class': 'form-control'}
      ),
      'spectrum_cutoff_high': forms.TextInput(
        attrs={'size': 6, 'placeholder': 'Max. M/Z', 'class': 'form-control'}
      ),
    }
    
class ViewCosineForm(forms.ModelForm):
  class Meta:
    model = SpectraCosineScore
    exclude = ('id',) 

class SpectraEditForm(forms.ModelForm):
  class Meta:
    model = Spectra
    exclude = ('id',) 

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

  
class AddLabGroupForm(forms.ModelForm):
  class Meta:
    model = LabGroup
    exclude = ()

class AddLibraryForm(forms.ModelForm):
  class Meta:
    model = Library
    exclude = ()
  
class LoadSqliteForm(forms.Form):
  user = forms.ModelMultipleChoiceField(
    queryset = user.objects.all(), to_field_name="username"
  )
  lab_name = forms.ModelMultipleChoiceField(
    queryset = LabGroup.objects.all(), to_field_name="lab_name"
  )
  library = forms.ModelMultipleChoiceField(
    queryset = Library.objects.all(), to_field_name="title"
  )
  
  file = forms.FileField()
  
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
  
  
class SpectraForm(forms.ModelForm):
  """ Form for handling addition of posts """
  
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
    
  class Meta:
    model = Spectra
    #fields = ('peaks', 'intensities')
    exclude = ()
    widgets = {
      'text': forms.Textarea(
        attrs={'rows': 2, 'cols': 40, 'placeholder': 'General description.'}
      ),
      'peaks': forms.Textarea(
        attrs={'rows': 2, 'cols': 40, 'placeholder': 'A comma-separated list, e.g., "167.06,179.07,193.07".'}
      ),
      'intensities': forms.Textarea(
        attrs={'rows': 2, 'cols': 40, 'placeholder': 'A comma-separated list, e.g., "0.4,0.2,0.6".'}
      ),
    }

class XmlForm(forms.ModelForm):
  class Meta:
    model = XML
    exclude = ('id',)
    # ~ fields = ('xml_hash','xml','manufacturer','model','ionization','analyzer','detector','instrument_metafile')
    
class MetadataForm(forms.ModelForm):
  """ Form for handling addition of metadata """
                            
  class Meta:
    model = Metadata
    exclude = ()
    widgets = {
      'cKingdom': forms.Textarea(
        attrs={'rows': 2, 'cols': 40, 'placeholder': ''}
      ),
      'cPhylum': forms.Textarea(
        attrs={'rows': 2, 'cols': 40, 'placeholder': ''}
      ),
      'cClass': forms.Textarea(
        attrs={'rows': 2, 'cols': 40, 'placeholder': ''}
      ),
      'cOrder': forms.Textarea(
        attrs={'rows': 2, 'cols': 40, 'placeholder': ''}
      ),
      'cGenus': forms.Textarea(
        attrs={'rows': 2, 'cols': 40, 'placeholder': ''}
      ),
      'cSpecies': forms.Textarea(
        attrs={'rows': 2, 'cols': 40, 'placeholder': ''}
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
  """ Form for adding comments"""

  text = forms.CharField(
    label="Comment",
    widget=forms.Textarea(attrs={'rows': 2})
  )

  def save(self, spectra, user):
    """ custom save method to create comment """

    comment = Comment.objects.create(text=self.cleaned_data.get('text', None), post=spectra, user=user)

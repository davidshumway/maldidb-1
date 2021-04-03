from django import forms
from .models import *
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
  strain_id = forms.ModelMultipleChoiceField(
    queryset = Metadata.objects.all(),
    to_field_name = "strain_id",
    required = False
  )
  spectra_id = forms.ModelMultipleChoiceField(
    queryset = Spectra.objects.all(),
    to_field_name = "id",
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

# ~ class SearchForm(forms.ModelForm):
  # ~ """Search by peaks/intensities, or upload mzXML or mzML file."""
  # ~ class Meta:
    # ~ model = Spectra
    # ~ exclude = ('id',)
  # ~ def __init__(self, *args, **kwargs):
    # ~ self.fields['metadata_strain_ids'] = forms.ModelChoiceField(queryset=Metadata.objects.all())

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

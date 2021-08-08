from django import forms
from .models import *
from spectra.models import *
from files.models import *
from django.contrib.auth import get_user_model
User = get_user_model()
from django.db.models import Q

class LibraryCollapseForm2(forms.Form):
  '''
  Collapse a library using default values.
  '''
  library = forms.ModelChoiceField(
    queryset = Library.objects.all(),
    required = True
  )
  
  def clean(self):
    data = self.cleaned_data
    if data['library'] not in Library.objects.filter(owner = self.request.user):
      raise forms.ValidationError(
        'Cannot access library or library does not exist!'
      )
    return data
    
  #class Meta:
  #  model = Library
  #  fields = ['id']
  
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
  lab = forms.ModelMultipleChoiceField(
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

class LibProfileForm(forms.ModelForm):
  class Meta:
    model = Library
    exclude = ('id', 'created_by')
  
  def __init__(self, *args, **kwargs):
    request = kwargs.pop('request')
    self.user = request.user
    super(LibProfileForm, self).__init__(*args, **kwargs)
    user = self.user
    user_labs = LabGroup.objects \
      .filter(Q(owners__in = [user]) | Q(members__in = [user]))
    self.fields['lab'].queryset = user_labs
    
class LabProfileForm(forms.ModelForm):
  class Meta:
    model = LabGroup
    exclude = ('id', 'lab_type')
  
# ~ class SearchForm(forms.ModelForm):
  # ~ '''Search by peaks/intensities, or upload mzXML or mzML file.'''
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
    exclude = ('created_by', 'lab_type')

class AddLibraryForm(forms.ModelForm):
  
  def __init__(self, *args, **kwargs):
    request = kwargs.pop('request')
    self.user = request.user
    super(AddLibraryForm, self).__init__(*args, **kwargs)
    user = self.user
    if request.user.is_authenticated:
      user_labs = LabGroup.objects \
        .filter(Q(owners__in = [user]) | Q(members__in = [user]))\
        .exclude(lab_type = 'user-uploads')
      # ~ q = Library.objects.filter( \
        # ~ Q(lab__in = user_labs) | \
        # ~ Q(created_by__exact = user)
      # ~ ).order_by('-id')
      # ~ self.fields['library_select'].queryset = q
      self.fields['lab'].queryset = user_labs
      
  class Meta:
    model = Library
    exclude = ('created_by',)

class MetadataModelChoiceField(forms.ModelChoiceField):
  def label_from_instance(self, obj):
    # ~ return "My Object #%i" % obj.id
    return obj.strain_id

class XmlForm(forms.ModelForm):
  class Meta:
    model = XML
    # ~ exclude = ('id','created_by','xml')
    exclude = ('id','xml',)
    # ~ fields = ('xml_hash','xml','manufacturer','model','ionization','analyzer','detector','instrument_metafile')
    
class MetadataForm(forms.ModelForm):
  '''
  Form for handling addition of metadata
  '''
  
  class Meta:
    model = Metadata
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
      'cFamily': forms.Textarea(
        attrs={'rows': 1, 'cols': 40, 'placeholder': ''}
      ),
      'cGenus': forms.Textarea(
        attrs={'rows': 1, 'cols': 40, 'placeholder': ''}
      ),
      'cSpecies': forms.Textarea(
        attrs={'rows': 1, 'cols': 40, 'placeholder': ''}
      ),
    }
  
  # ~ def clean(self):
    # ~ cleaned_data = super().clean()
    
    # ~ # Adds files. If files don't exist, adds blank files.
    # ~ filenames = cleaned_data['filenames'].split('|')
    # ~ for file in filenames:
      # ~ uf, bool_created = UserFile.objects.get_or_create(
        # ~ filename = file,
        # ~ library = cleaned_data['library'])
      # ~ cleaned_data['files'].add(uf)
    # ~ #if self.instance:
    # ~ #  # ~ ####cleaned_data['quantity'] += self.instance.quantity
    # ~ return cleaned_data

class LocaleForm(forms.ModelForm):
  class Meta:
    model = Locale
    exclude = ()

class VersionForm(forms.ModelForm):
  class Meta:
    model = Version
    exclude = ()
    
class CommentForm(forms.Form):
  '''
  Form for adding comments
  '''

  text = forms.CharField(
    label = "Comment",
    widget = forms.Textarea(attrs = {'rows': 2})
  )

  def save(self, spectra, user):
    '''
    custom save method to create comment
    '''
    comment = Comment.objects.create(
      text = self.cleaned_data.get('text', None),
      post = spectra,
      user = user
    )

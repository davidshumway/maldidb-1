from django import forms
from .models import *
from django.contrib.auth import get_user_model
from chat.models import Library
# ~ User = get_user_model()

class LibCompareForm(forms.ModelForm):
  library = forms.ModelMultipleChoiceField(
    queryset = Library.objects.all(),
    #multiple = True
    widget = forms.Select(
      attrs = {'class': 'custom-select', 'multiple': True,
        'style': 'height:400px;'}
    )
  )
  class Meta:
    model = Library
    fields = ['library']
  
class SpectraEditForm(forms.ModelForm):
  class Meta:
    model = Spectra
    exclude = ('id','created_by',) 

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

from django import forms
from .models import *
from django.contrib.auth import get_user_model
from chat.models import Library

class LibCompareForm(forms.ModelForm):
  library = forms.ModelMultipleChoiceField(
    queryset = Library.objects.all(),
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
  '''
  Form for handling addition of spectra
  '''
  
  class Meta:
    model = Spectra
    exclude = ('id',)
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

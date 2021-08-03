from django import forms
from chat.models import Library, LabGroup
import os

class LoadSqliteForm(forms.Form):
  lab = forms.ModelChoiceField(
    queryset = LabGroup.objects.all(), to_field_name="lab_name"
  )
  library = forms.ModelChoiceField(
    queryset = Library.objects.all(), to_field_name="title"
  )  
  choices = [
    ('single', 'Upload a single IDBac SQLite file'),
    ('r01', 'Load one or more hosted IDBac R01 data files'),
  ]
  upload_type = forms.CharField(
    label = 'Upload type',
    widget = forms.RadioSelect(choices = choices),
    required = True,
    initial = 'single')
  file = forms.FileField(required = False,
    label = 'Select an IDBac SQLite file to upload')
  
  files = []
  for filename in os.listdir('/home/app/web/r01data/'):
    if '.sqlite' in filename:
      files.append((filename, filename))
  r01data = forms.MultipleChoiceField(choices = files, required = False)

  def clean(self):
    data = self.cleaned_data
    if data.get('file') == None and data.get('upload_type') == 'single':
      raise forms.ValidationError(
        'Select a file to upload!'
      )
    elif data.get('r01data') == None and data.get('upload_type') == 'r01':
      raise forms.ValidationError(
        'Select a file to upload!'
      )
    else:
      return data

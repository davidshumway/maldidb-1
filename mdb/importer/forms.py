from django import forms
from chat.models import Library, LabGroup
  
class LoadSqliteForm(forms.Form):
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
  privacy_level = forms.MultipleChoiceField(choices = [
    ('PB', 'Public'),
    ('PR', 'Private'),
  ])
  
  def clean(self):
    data = self.cleaned_data
    #print('add form', data)
    if data.get('file') == None and data.get('upload_type') == 'single':
      raise forms.ValidationError(
        'Select a file to upload!'
      )
    else:
      return data

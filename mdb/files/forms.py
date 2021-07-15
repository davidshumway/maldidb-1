from django import forms
from chat.models import *
from spectra.models import *
from files.models import UserFile
from dal import autocomplete
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.crypto import get_random_string # for random library
User = get_user_model()

class FileUploadForm(forms.Form):
  '''
  Performs similar tasks as spectra.forms.SpectraLibraryForm
  
  TODO: This form and spectra.forms.SpectraLibraryForm should inherit
    from an abstract parent form.
  '''
  file = forms.FileField(
    label = 'Upload one or more files',
    required = False,
    widget = forms.ClearableFileInput(attrs={'multiple': True})
  )
  number_files = forms.IntegerField(widget = forms.HiddenInput(),
    initial = 0)
    
  # save to existing library
  library_select = forms.ModelChoiceField(
    queryset = Library.objects.all(),
    to_field_name = 'title',
    required = False,
    widget = forms.Select(
      attrs = {
        'class': 'custom-select'}
    ),
    empty_label = 'Choose...'
  )
  
  library_create_new = forms.CharField(
    required = False,
    help_text = 'Enter a name for the new library',
    widget = forms.TextInput(
      attrs = {
        'class': 'form-control', 'placeholder': 'Enter a library title ...'}
    )
  )
  library_save_type = forms.CharField(label = '',
    widget = forms.RadioSelect(choices = [
      ('RANDOM', 'Random'),
      ('NEW', 'New'),
      ('EXISTING', 'Existing'),
    ])
  )
  
  use_filenames = forms.BooleanField(
    required = False,
    initial = True,
    label = 'Use filenames for strain IDs?')
  
  file_strain_ids = forms.CharField(
    required = False,
    widget = forms.Textarea(attrs = {'rows': 6, 'style': 'width:100%;'}),
    # Bug? Setting disabled causes the form to ignore any input here.
    # ~ disabled = True
    )
    
  preprocess = forms.BooleanField(
    required = True,
    initial = True,
    label = 'Perform spectra preprocessing?',
    disabled = True)
      
  # ~ class Meta:
    # ~ model = UserFile
    # ~ exclude = ('id', 'owner', 'upload_date', 'extension')
    #custom-select
    # ~ widgets = {
      # ~ 'lab': forms.Select(
        # ~ attrs = {'class': 'custom-select'}
      # ~ ),
    # ~ }
  
  # ~ def __init__(self, *args, **kwargs):
    # ~ request = kwargs.pop('request')
    # ~ self.user = request.user
    # ~ super(SpectraLibraryForm, self).__init__(*args, **kwargs)
    # ~ user = self.user
    # ~ if request.user.is_authenticated:
      # ~ user_labs = LabGroup.objects \
        # ~ .filter(Q(owners__in = [user]) | Q(members__in = [user]))
      # ~ q = Library.objects.filter( \
        # ~ Q(lab__in = user_labs) | \
        # ~ Q(created_by__exact = user)
      # ~ ).order_by('-id')
      # ~ self.fields['library_select'].queryset = q
  
  def clean_file_strain_ids(self):
    d = self.cleaned_data['file_strain_ids']
    if self.cleaned_data['use_filenames'] is False:
      try:
        if self.cleaned_data['number_files'] is False:
          raise forms.ValidationError('Field "number_files" missing!')
      except:
        raise forms.ValidationError('Field "number_files" missing!')
      if d.strip() == '':
        raise forms.ValidationError(
          'List of filenames must not be empty!'
        )
      import re
      x = re.sub('[\r\n]+', '\n', d.strip())
      x = x.split('\n')
      # Entries == form entries
      if len(x) != self.cleaned_data['number_files']:
        raise forms.ValidationError(
          'Number of filenames ({}) does not match number of files ({})!'
          .format(len(x), self.cleaned_data['number_files']))
      # < 255
      for tmpmd in x:
        if len(tmpmd.strip()) > 255:
          raise forms.ValidationError(
            'Filenames contains an entry > 255 characters!')
      # Unique, e.g. [1,1] != {1}
      if len(set(x)) != len(x):
        raise forms.ValidationError(
            'Filenames are not unique!')
    return d
    
  def clean(self):
    '''
    Adds "library" key
    '''
    d = super().clean()
    # ~ cleaned_data['cKingdom'] = Metadata.objects.none()
    # ~ d['cKingdom'] = Metadata.objects.filter(cKingdom__exact = 'Bacteria')
    # ~ d['cClass'] = Metadata.objects.filter(cClass__exact = 'Gammaproteobacteria')
    # ~ print(f'clean{d}')
    
    # user's lab
    user_lab, created = LabGroup.objects.get_or_create(
      lab_name = self.user.username + '\'s default lab',
      user_default_lab = True,
      owners__in = [self.user])
    if created:
      user_lab.owners.add(self.user)
      user_lab.members.add(self.user)
      user_lab.save()
    
    # validate upload library
    if d.get('library_save_type') == 'RANDOM':
      title = get_random_string(8)
      # (safe check) Checks random entry doesn't exist
      x = False
      c = 100
      while x is False and c > 0:
        c -= 1
        n = Library.objects.filter(
          created_by = self.user,
          title = title
        )
        if len(n) == 0:
          x = True
          new_lib = Library.objects.create(
            created_by = self.user,
            title = title,
            lab = user_lab,
            privacy_level = 'PR'
          )
          d['library'] = new_lib
    elif d.get('library_save_type') == 'NEW':
      # TODO: Library can have same title by same user but saved
      #       in a different lab group.
      n = Library.objects.filter(
        created_by = self.user,
        title = d.get('library_create_new'),
        privacy_level = 'PR'
      )
      if len(n) != 0:
        raise forms.ValidationError(
          'Library title already exists!'
        )
      else:
        new_lib = Library.objects.create(
          created_by = self.user,
          title = d.get('library_create_new'),
          lab = user_lab,
          privacy_level = 'PR'
        )
        d['library'] = new_lib
    elif d.get('library_save_type') == 'EXISTING':
      d['library'] = d['library_select']
    return d

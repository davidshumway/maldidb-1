from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator

class UserFile(models.Model):
  '''
  Spectra files uploaded by users.
  
  -- May be associated with one or more Spectra.
  '''
  owner = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete = models.CASCADE,
    blank = False,
    null = False)
  file = models.FileField(
    upload_to = 'uploads/',
    validators = [
      FileExtensionValidator(allowed_extensions = ['mzml', 'mzxml', 'fid'])
    ]
  )
  upload_date = models.DateTimeField(auto_now_add = True, blank = False)
  #extension = models.CharField(max_length = 255, blank = True, null = True)
  spectra = models.ManyToManyField('chat.Spectra', blank = True)
  # ~ spectra = models.ManyToManyField('Spectra', blank = True)

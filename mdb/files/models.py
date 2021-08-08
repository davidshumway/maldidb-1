from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from spectra.models import *
import os

class UserFile(models.Model):
  '''
  Spectra and metadata files uploaded by users
  
  Owner is optional allows for anonymous user uploads.
  
  '''
  owner = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete = models.CASCADE,
    blank = True,
    null = True)
  file = models.FileField(
    upload_to = 'uploads/',
    validators = [
      FileExtensionValidator(
        allowed_extensions = ['mzml', 'mzxml', 'fid', 'csv'])
    ]
  )
  extension = models.CharField(max_length = 255, blank = True)
  upload_date = models.DateTimeField(auto_now_add = True, blank = False)

  #spectra = models.ManyToManyField('spectra.Spectra', blank = True)
  # ~ class Meta:
    # ~ unique_together= (('file', 'library'),)
  
  # ~ def extension(self):
    # ~ name, extension = os.path.splitext(self.file.name)
    # ~ return extension

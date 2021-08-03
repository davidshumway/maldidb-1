from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from spectra.models import *

class UserFile(models.Model):
  '''
  Spectra files uploaded by users.
  
  May be associated with one or more Spectra.
  
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
  upload_date = models.DateTimeField(auto_now_add = True, blank = False)
  spectra = models.ManyToManyField('spectra.Spectra', blank = True)

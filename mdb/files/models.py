from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from spectra.models import *
import os
from uuid import uuid4
from django.db import models
from django.core.files.storage import FileSystemStorage

class OverwriteStorage(FileSystemStorage):
  def _save(self, name, content):
    if self.exists(name):
      self.delete(name)
    return super(OverwriteStorage, self)._save(name, content)
  def get_available_name(self, name, max_length):
    return name

class UserFile(models.Model):
  '''
  Spectra and metadata files uploaded by users
  
  -- Owner is optional allows for anonymous user uploads.
  '''
  owner = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete = models.CASCADE,
    blank = True,
    null = True)
  file = models.FileField(
    # ~ upload_to = path_and_rename,
    upload_to = 'uploads/',
    validators = [
      FileExtensionValidator(
        allowed_extensions = ['mzml', 'mzxml', 'fid', 'csv'])
    ],
    storage = OverwriteStorage()
  )
  extension = models.CharField(max_length = 255, blank = True)
  upload_date = models.DateTimeField(auto_now_add = True, blank = False)
  library = models.ForeignKey('chat.Library', on_delete = models.CASCADE,
    blank = False, null = False)
  
  # ~ def replace_video(self):
    # ~ self.file.save(os.path.basename(self.file.path), File(open(video_path ,"wb")), save=True)
    # ~ os.remove(video_path)
    # ~ os.remove(old_path)

  #spectra = models.ManyToManyField('spectra.Spectra', blank = True)
  class Meta:
    unique_together= (('file', 'library'),)
  
  # ~ def extension(self):
    # ~ name, extension = os.path.splitext(self.file.name)
    # ~ return extension

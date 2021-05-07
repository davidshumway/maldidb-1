from django.db import models
from django.conf import settings
import uuid
from django.urls import reverse
from spectra.models import *

# For model triggers
# ~ from django.db.models.signals import post_save, m2m_changed
# ~ from django.dispatch import receiver
# ~ from django.utils import timezone

# ~ class UserLogs(models.Model):
  # ~ '''
  # ~ -- Capture errors in SQLite and file imports
  # ~ '''
  # ~ owner = models.ForeignKey(
    # ~ settings.AUTH_USER_MODEL,
    # ~ on_delete = models.CASCADE,
    # ~ blank = False,
    # ~ null = False)
  # ~ log_date = models.DateTimeField(auto_now_add = True, blank = False)
  # ~ title = models.CharField(max_length = 255, blank = False)
  # ~ description = models.TextField(blank = False)

class UserTask(models.Model):
  '''
  '''
  owner = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete = models.CASCADE,
    blank = False,
    null = False)
  # ~ task_complete = models.BooleanField(blank = False, null = False,
    # ~ default = False)
  task_choices = [
    ('idbac_sql', 'Insert IDBac SQLite data to database'),
    ('spectra', 'Add spectra files to database'),
    ('preprocess', 'Preprocess spectra'),
    ('collapse', 'Collapse replicates'),
    ('cos_search', 'Cosine score search'),
  ]
  task_description = models.CharField(
    max_length = 255,
    choices = task_choices,
    blank = True,
    null = True
  )
  statuses = models.ManyToManyField('UserTaskStatus')
  last_modified = models.DateTimeField(auto_now_add = True, blank = False)
  
#@receiver(m2m_changed, sender = UserTask, dispatch_uid = None)
# ~ @receiver(m2m_changed, sender = UserTask.statuses.through)
# ~ def update_user_task(sender, instance, action, **kwargs):
  # ~ '''Update last_modified on UserTask when m2m (statuses) field is updated.'''
  # ~ if action in ['post_add', 'post_remove', 'post_clear']:
    # ~ instance.last_modified = timezone.now()
    # ~ m2m_changed.disconnect(update_user_task, sender = UserTask)
    # ~ instance.save()
    # ~ m2m_changed.connect(update_user_task, sender = UserTask)
  
# Another model to 
class UserTaskStatus(models.Model):
  '''Describe lifecycle events of user tasks.
  
  -- An extra field to optionally further explain the status.
  -- Each time a new status is created, trigger last_modified on UserTask
     to update.
  -- @user_task: FK, Link back to UserTask containing this status (m2m)
  '''
  status_choices = [
    ('start', 'Started'),
    ('run', 'Running'),
    ('complete', 'Completed'),
    ('error', 'Completed - Error'),
    ('info', 'Info') # a status to report task progress
  ]
  status = models.CharField(
    max_length = 255,
    choices = status_choices,
    blank = False,
    null = False
  )
  status_date = models.DateTimeField(auto_now_add = True, blank = False)
  extra = models.TextField(blank = True, null = True)
  user_task = models.ForeignKey(
    'UserTask',
    # ~ related_name = '',
    on_delete = models.CASCADE,
    blank = True, null = True)

class PrivacyLevel(models.Model):
  ''' Privacy level for library, spectra, etc.
  '''
  PUBLIC = 'PB'
  PRIVATE = 'PR'
  privacyChoices = [
    (PUBLIC, 'Public'),
    (PRIVATE, 'Private'),
  ]
  level = models.CharField(
    max_length = 2,
    choices = privacyChoices,
    default = PUBLIC,
  )
  
class Library(models.Model):
  '''
  '''
  created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    # ~ related_name = 'created_by',
    on_delete = models.CASCADE,
    blank = True,
    null = True)
  
  lab_name = models.ForeignKey('LabGroup', on_delete = models.CASCADE)
  
  title = models.CharField(max_length = 200)
  description = models.TextField(blank = True)
  
  PUBLIC = 'PB'
  PRIVATE = 'PR'
  privacyChoices = [
    (PUBLIC, 'Public'),
    (PRIVATE, 'Private'),
  ]
  privacy_level = models.CharField(
    max_length = 2,
    choices = privacyChoices,
    default = PUBLIC,
  )
  
  GOLD = 'GO'
  SILVER = 'SI'
  BRONZE = 'BR'
  qualChoices = [
    (GOLD, 'Gold'),
    (SILVER, 'Silver'),
    (BRONZE, 'Bronze'),
  ]
  quality_rating = models.CharField(
    max_length = 2,
    choices = qualChoices,
    default = BRONZE,
  )
  
  def __str__(self):
    #return f"{self.user.username}'s library"
    return self.title
  
  def get_fields(self):
    return [(field.verbose_name, field.value_to_string(self)) for field in Library._meta.fields]
  
  def get_absolute_url(self):
    return reverse('chat:view_library', args = (self.id,))
      
class LabGroup(models.Model):
  '''At least one owner. Zero or more members.'''
  lab_name = models.CharField(max_length = 200)
  lab_description = models.TextField(blank = True)
  owners = models.ManyToManyField(settings.AUTH_USER_MODEL)
  members = models.ManyToManyField(settings.AUTH_USER_MODEL,
    blank = True,
    related_name = "lab_members")
  
    #models.ForeignKey(
    #settings.AUTH_USER_MODEL,
    #on_delete = models.CASCADE)
  
  def __str__(self):
    return self.lab_name
  
  def get_fields(self):
    return [(field.verbose_name, field.value_to_string(self)) for field in LabGroup._meta.fields]
    
  def get_absolute_url(self):
    return reverse('chat:view_lab', args = (self.id,))

# ~ @receiver(post_save, sender = LabGroup, dispatch_uid = None)
# ~ def update_stock(sender, instance, **kwargs):
  # ~ '''Add each owner to the group as a member when creating the group.
  
  # ~ TODO: This only adds the owners when the LabGroup is first created.
        # ~ When updating the lab group, the form's values override this.'''
  # ~ for owner in instance.owners.all():
    # ~ instance.members.add(owner)
  # ~ post_save.disconnect(update_stock, sender = LabGroup)
  # ~ instance.save()
  # ~ post_save.connect(update_stock, sender = LabGroup)
  
class Metadata(models.Model):
  ''' UNIQUE(strain_id).
  -- Removing unique from strain_id ???
  -- Todo: Add unique(strain_id, library)
  '''
  # ~ strain_id = models.TextField(blank = True)
  strain_id = models.CharField(max_length = 255, blank = True) #, unique = True)
  genbank_accession = models.CharField(max_length = 255, blank = True)
  ncbi_taxid = models.CharField(max_length = 255, blank = True)
  cKingdom = models.CharField(max_length = 255, blank = True)
  cPhylum = models.CharField(max_length = 255, blank = True)
  cClass = models.CharField(max_length = 255, blank = True)
  cOrder = models.CharField(max_length = 255, blank = True)
  cGenus = models.CharField(max_length = 255, blank = True)
  cSpecies = models.CharField(max_length = 255, blank = True)
  maldi_matrix = models.CharField(max_length = 255, blank = True)
  dsm_cultivation_media = models.CharField(max_length = 255, blank = True)
  cultivation_temp_celsius = models.CharField(max_length = 255, blank = True)
  cultivation_time_days = models.CharField(max_length = 255, blank = True)
  cultivation_other = models.CharField(max_length = 255, blank = True)
  
  user_firstname_lastname = models.CharField(max_length = 255, blank = True)
  user_orcid = models.CharField(max_length = 255, blank = True)
  pi_firstname_lastname = models.CharField(max_length = 255, blank = True)
  pi_orcid = models.CharField(max_length = 255, blank = True)
  
  dna_16s = models.CharField(max_length = 255, blank = True)
  
  created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete = models.CASCADE,
    blank = True,
    null = True)
  
  lab_name = models.ForeignKey(
    'LabGroup',
    on_delete = models.CASCADE,
    blank = True,
    null = True)
    
  library = models.ForeignKey(
    'Library',
    on_delete = models.CASCADE,
    blank = True,
    null = True)
    
  def get_fields(self):
    return [(field.verbose_name, field.value_to_string(self)) for field in Metadata._meta.fields]
  
  def __str__(self):
    #return f"{self.user.username}'s library"
    return self.strain_id
  
  def get_absolute_url(self):
    return reverse('chat:view_metadata', args = (self.strain_id,))
      
class XML(models.Model):
  '''UNIQUE(xml_hash) ---- removed '''
  xml_hash = models.CharField(max_length = 255, blank = True) #, unique = True
  # ~ xml             BLOB,
  #########################
  xml = models.TextField(blank = True)
  
  manufacturer = models.CharField(max_length = 255, blank = True)
  model = models.CharField(max_length = 255, blank = True)
  
  ionization = models.CharField(max_length = 255, blank = True)
  analyzer = models.CharField(max_length = 255, blank = True)
  detector = models.CharField(max_length = 255, blank = True)
  # ~ instrument_metafile BLOB,
  #############################
  instrument_metafile = models.TextField(blank = True)
  
  created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete = models.CASCADE,
    blank = True,
    null = True)
  
  lab_name = models.ForeignKey(
    'LabGroup',
    on_delete = models.CASCADE,
    blank = True,
    null = True)
  
  def get_fields(self):
    return [(field.verbose_name, field.value_to_string(self)) for field in XML._meta.fields]
  
  def get_absolute_url(self):
    return reverse('chat:view_xml', args = (self.xml_hash,))
  
  def __str__(self):
    #return f"{self.user.username}'s library"
    return self.xml_hash
    
class Version(models.Model):
  idbac_version = models.CharField(max_length = 200, blank = True)
  r_version = models.TextField(blank = True)
  db_version = models.CharField(max_length = 200, blank = True)
  
  def get_fields(self):
    return [(field.verbose_name, field.value_to_string(self)) for field in Version._meta.fields]
    
class Locale(models.Model):
  locale = models.TextField(blank = True)
  
  def get_fields(self):
    return [(field.verbose_name, field.value_to_string(self)) for field in Locale._meta.fields]
    
class Comment(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name = 'comments', on_delete = models.CASCADE)
  spectra = models.ForeignKey('spectra.Spectra', related_name = 'comments', on_delete = models.CASCADE)
  text = models.TextField(max_length = 2048, blank = True)
  comment_date = models.DateTimeField(auto_now_add = True)

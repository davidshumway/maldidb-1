from django.db import models
from django.conf import settings
import uuid
from django.urls import reverse

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
    ('idbac_sql','Insert IDBac SQLite data to database'),
    ('spectra','Add spectra files to database'),
    ('preprocess','Preprocess spectra'),
    ('collapse','Collapse replicates'),
    ('cos_search','Cosine score search'),
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
  
class AbstractCosineScore(models.Model):
  score = models.DecimalField(
    max_digits = 10, decimal_places = 6, blank = False)
    
  class Meta:
    abstract = True

class CollapsedCosineScore(AbstractCosineScore):
  spectra1 = models.ForeignKey(
    'CollapsedSpectra',
    related_name = 'spectra1',
    on_delete = models.CASCADE)
  spectra2 = models.ForeignKey(
    'CollapsedSpectra',
    related_name = 'spectra2',
    on_delete = models.CASCADE)
  # ~ score = models.DecimalField(
    # ~ max_digits = 10, decimal_places = 6, blank = False)
      
class SpectraCosineScore(AbstractCosineScore):
  spectra1 = models.ForeignKey(
    'Spectra',
    related_name = 'spectra1',
    on_delete = models.CASCADE)
  spectra2 = models.ForeignKey(
    'Spectra',
    related_name = 'spectra2',
    on_delete = models.CASCADE)
  # ~ score = models.DecimalField(
    # ~ max_digits = 10, decimal_places = 6, blank = False)

class SearchSpectraCosineScore(AbstractCosineScore):
  spectra1 = models.ForeignKey(
    'SearchSpectra',
    related_name = 'search_spectra1',
    on_delete = models.CASCADE)
  spectra2 = models.ForeignKey(
    'Spectra',
    related_name = 'search_spectra2',
    on_delete = models.CASCADE)
    
class AbstractSpectra(models.Model):
  # ~ privacy_level = models.ForeignKey(
    # ~ 'PrivacyLevel',
    # ~ on_delete = models.CASCADE,
    # ~ blank = True)
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
    blank = True,
    null = True
  )
  
  library = models.ForeignKey(
    'Library',
    on_delete = models.CASCADE,
    blank = True,
    null = True)
  
  created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    # ~ related_name = 'created_by',
    on_delete = models.CASCADE,
    blank = True,
    null = True)
  
  lab_name = models.ForeignKey(
    'LabGroup',
    on_delete = models.CASCADE,
    blank = True,
    null = True)
  
  # Averaged m/z and intensity values in case of collapse spectra
  # ~ peak_matrix = models.TextField(blank = True)
  # ~ spectrum_intensity = models.TextField(blank = True)
  
  peak_mass = models.TextField(blank = True,
    help_text = 'A list of comma separated values, e.g., "1,2,3"')
  peak_intensity = models.TextField(blank = True,
    help_text = 'A list of comma separated values, e.g., "1,2,3"')
  peak_snr = models.TextField(blank = True,
    help_text = 'A list of comma separated values, e.g., "1,2,3"')
  
  spectrum_mass_hash = models.CharField(max_length = 255, blank = True)
  spectrum_intensity_hash = models.CharField(max_length = 255, blank = True)
  
  xml_hash = models.ForeignKey(
    'XML',
    db_column = 'xml_hash',
    on_delete = models.CASCADE, 
    blank = True,
    null = True)
    
  strain_id = models.ForeignKey(
    'Metadata',
    db_column = 'strain_id',
    on_delete = models.CASCADE,
    blank = True,
    null = True)
  
  # ~ unique_together = (
    # ~ strain_id,
    # ~ spectrum_mass_hash,
    # ~ spectrum_intensity_hash
  # ~ )
  
  class Meta:                                                                 
    abstract = True                                                         
  
  def get_absolute_url(self):
    return reverse('chat:view_spectra', args = (self.id,))
  
class CollapsedSpectra(AbstractSpectra):
  '''
  Inherits strain_id
  Pipeline cols: peak_percent_presence, lower_mass_cutoff,
    upper_mass_cutoff, min_snr, tolerance
  Remove lower and upper mass cutoff.
  MALDIQuant docs: 4.10 Feature Matrix We choose a very low
    signal-to-noise ratio to keep as much features as possible.
    To remove some false positive peaks we remove less frequent peaks.
  '''
  # e.g., collapsed_spectra.add(s1, s2, ..., sN)
  collapsed_spectra = models.ManyToManyField('Spectra')
  
  peak_percent_presence = models.DecimalField( # e.g. 70.00%
    max_digits = 4, decimal_places = 1, blank = False, default = 70.0)
  # ~ lower_mass_cutoff = models.IntegerField(blank = True) #e.g. 0
  # ~ upper_mass_cutoff = models.IntegerField(blank = True) #e.g. 6000
  
  min_snr = models.DecimalField(
    max_digits = 4, decimal_places = 2, blank = False, default = 0.25) #e.g. 0-1???
  tolerance = models.DecimalField(
    max_digits = 10, decimal_places = 3, blank = False, default = 0.002)
  
  # spectra is protein(>6k) OR small molecule(<6k),
  # aka tofMode or acquisitionOperatorMode (REFLECTOR/LINEAR)
  # spectraContent is "protein" in R function.
  spectraChoices = [
    ('PR', 'Protein'),
    ('SM', 'Small Molecule'),
  ]
  spectra_content = models.CharField(
    max_length = 2,
    choices = spectraChoices,
    default = 'PR',
  )
  
  generated_date = models.DateTimeField(auto_now_add = True, blank = True)


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
 
class SearchSpectra(AbstractSpectra):
  peak_mass = models.TextField(blank = True)
  peak_intensity = models.TextField(blank = True)
  peak_snr = models.TextField(blank = True)
  created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    # ~ related_name = 'created_by',
    on_delete = models.CASCADE,
    blank = True,
    null = True)
  
# ~ class Replicates(models.Model):
  # ~ '''
  # ~ Each entry corresponds to a list of 1-N spectra for a given strain_id.
  
  # ~ E.g., strain_id = 'B009', replicates = [spectra.1, spectra.2, ...].
  # ~ '''
  # ~ strain_id = models.ForeignKey(
    # ~ 'Metadata',
    # ~ db_column = 'strain_id',
    # ~ on_delete = models.CASCADE,
    # ~ blank = False,
    # ~ null = False
  # ~ )
  # ~ replicates = models.ManyToManyField('Spectra') # points to 1-N replicates
  # ~ spectraChoices = [
    # ~ ('PR', 'Protein'),
    # ~ ('SM', 'Small Molecule'),
  # ~ ]
  # ~ spectra_content = models.CharField(
    # ~ max_length = 2,
    # ~ choices = spectraChoices,
    # ~ blank = False,
    # ~ null = False
  # ~ )
  
class Spectra(AbstractSpectra):
  ''' Spectra Model
  
  -- Sqlite NUMERIC data type: 'Type affinity is the recommended type
  of data stored in a column. However, you still can store any type of
  data as you wish, these types are recommended not required.'
  -- DecimalField: Using parameters max_digits = 30, decimal_places = 20
  -- IntegerField: -2147483648 to 2147483647
  
  -- Original columns that were integer / numeric:
      time_delay                            INTEGER,
      time_delta                            NUMERIC,
      laser_attenuation                     INTEGER,
      mass_error                            NUMERIC,
      laser_shots                           INTEGER,
      min_mass                              INTEGER,
      ignore                               INTEGER,
      number                               INTEGER,
  -- Original name of cId is "id"
  -- acquisition_date: Using CharField rather than date field for now
  '''
  
  
  # UNIQUE(strain_id, spectrum_mass_hash, spectrum_intensity_hash) 
  
  
  # Each spectra belongs to one library.
  # Each library contains many spectra.
  # ~ library = models.ForeignKey('Library', on_delete = models.CASCADE)
  
  # ~ created_by = models.ForeignKey(
    # ~ settings.AUTH_USER_MODEL,
    ###related_name = 'uploaded_by',
    # ~ on_delete = models.CASCADE)
  
  # ~ privacy_level = models.ForeignKey(
    # ~ 'PrivacyLevel',
    # ~ on_delete = models.CASCADE,
    # ~ blank = True)
    
  picture = models.ImageField(upload_to = 'spectra_images', blank = True)
  description = models.TextField(max_length = 2048, blank = True)
  posted_date = models.DateTimeField(auto_now_add = True, blank = True)
  
  max_mass = models.IntegerField(blank = True, null = True)
  min_mass = models.IntegerField(blank = True, null = True)
  acquisition_date = models.CharField(max_length = 255, blank = True, null = True)
  acquisition_mode = models.CharField(max_length = 255, blank = True, null = True)
  
  # ~ tof_mode = models.CharField(
    # ~ max_length = 255,
    # ~ choices = [
      # ~ ('REFLECTOR', 'Reflector'),
      # ~ ('LINEAR', 'Linear'),
    # ~ ],
    # ~ blank = True, null = True 
  # ~ )
  
  spot = models.CharField(max_length = 255, blank = True, null = True)
  
  class Meta:
    indexes = [
      #models.Index(fields = ['tof_mode',]),
    ]

  def __str__(self):
    if self.created_by != None:
      return f"{self.created_by.username}'s spectra"
    else: return 'Created by an anonymous user'
  
  def get_fields(self):
    return [(field.verbose_name, field.value_to_string(self)) for field in Spectra._meta.fields]
  
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
  ''' The comments Models '''

  user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name = 'comments', on_delete = models.CASCADE)
  spectra = models.ForeignKey(Spectra, related_name = 'comments', on_delete = models.CASCADE)
  text = models.TextField(max_length = 2048, blank = True)
  comment_date = models.DateTimeField(auto_now_add = True)

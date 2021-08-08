from django.db import models
from django.conf import settings
import uuid
from django.urls import reverse
from spectra.models import *
from files.models import *

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
    blank = True, null = True)
  
  lab = models.ForeignKey(
    'LabGroup', on_delete = models.CASCADE,
    blank = False, null = False)
  
  user_files = models.ManyToManyField(UserFile,
    blank = True)
    
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
    return self.title
  
  def get_fields(self):
    return [(field.verbose_name, field.value_to_string(self)) for field in Library._meta.fields]
  
  def get_absolute_url(self):
    return reverse('chat:view_library', args = (self.id,))
      
class LabGroup(models.Model):
  '''
  
  Labs: At least one owner. Zero or more members.
  TODO: Lab privacy level
  
  '''
  lab_name = models.CharField(max_length = 200)
  lab_description = models.TextField(blank = True)
  owners = models.ManyToManyField(settings.AUTH_USER_MODEL,
    blank = True,
    related_name = 'lab_owners')
  members = models.ManyToManyField(settings.AUTH_USER_MODEL,
    blank = True,
    related_name = 'lab_members')
  lab_type = models.CharField(
    max_length = 20,
    choices = [
      ('user-uploads', 'User uploads lab'),
      ('user-default', 'User default lab'),
      ('other', 'Other lab'), # any other lab
    ],
    default = 'other',
  )
  
  # ~ user_default_lab = models.BooleanField( # dedicated lab for every user
    # ~ blank = True,
    # ~ default = False)
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
  '''
  -- files: Associates with one or more user files
  -- filenames: "|" separated raw filenames from a csv file
  '''
  # ~ strain_id = models.TextField(blank = True)
  strain_id = models.CharField(max_length = 255, blank = True) #, unique = True)
  genbank_accession = models.CharField(max_length = 255, blank = True)
  ncbi_taxid = models.CharField(max_length = 255, blank = True)
  cKingdom = models.CharField(max_length = 255, blank = True)
  cPhylum = models.CharField(max_length = 255, blank = True)
  cClass = models.CharField(max_length = 255, blank = True)
  cOrder = models.CharField(max_length = 255, blank = True)
  cFamily = models.CharField(max_length = 255, blank = True)
  cGenus = models.CharField(max_length = 255, blank = True)
  cSpecies = models.CharField(max_length = 255, blank = True)
  cSubspecies = models.CharField(max_length = 255, blank = True)
  maldi_matrix = models.CharField(max_length = 255, blank = True)
  dsm_cultivation_media = models.CharField(max_length = 255, blank = True)
  cultivation_temp_celsius = models.CharField(max_length = 255, blank = True)
  cultivation_time_days = models.CharField(max_length = 255, blank = True)
  cultivation_other = models.CharField(max_length = 255, blank = True)
  
  user_firstname_lastname = models.CharField(max_length = 255, blank = True)
  user_orcid = models.CharField(max_length = 255, blank = True)
  pi_firstname_lastname = models.CharField(max_length = 255, blank = True)
  pi_orcid = models.CharField(max_length = 255, blank = True)
  
  dna_16s = models.TextField(blank = True)
  # ~ dna_16s = models.CharField(max_length = 255, blank = True)
  
  created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete = models.CASCADE,
    blank = True,
    null = True)
  
  # ~ lab = models.ForeignKey( # unnecessary
    # ~ 'LabGroup',
    # ~ on_delete = models.CASCADE,
    # ~ blank = True,
    # ~ null = True)
    
  library = models.ForeignKey('Library',
    on_delete = models.CASCADE,
    blank = True,
    null = True)
  
  files = models.ManyToManyField(UserFile,
    blank = True,
    related_name = 'user_files')
  
  filenames = models.TextField(blank = True)
  
  class Meta:
    unique_together= (('strain_id', 'library'),)
            
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
  
  # ~ lab = models.ForeignKey(
    # ~ 'LabGroup',
    # ~ on_delete = models.CASCADE,
    # ~ blank = True,
    # ~ null = True)
  library = models.ForeignKey(
    'Library',
    on_delete = models.CASCADE,
    blank = True,
    null = True)
  
  class Meta:
    unique_together= (('xml_hash', 'library'),)
    
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

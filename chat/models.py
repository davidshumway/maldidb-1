from django.db import models
from django.conf import settings
import uuid
from django.urls import reverse

    

class AbstractCosineScore(models.Model):
  score = models.DecimalField(
    max_digits=10, decimal_places=6, blank=False)
    
  class Meta:
    abstract = True

class CollapsedCosineScore(AbstractCosineScore):
  spectra1 = models.ForeignKey(
    'CollapsedSpectra',
    related_name='spectra1',
    on_delete=models.CASCADE)
  spectra2 = models.ForeignKey(
    'CollapsedSpectra',
    related_name='spectra2',
    on_delete=models.CASCADE)
  # ~ score = models.DecimalField(
    # ~ max_digits=10, decimal_places=6, blank=False)
      
class SpectraCosineScore(AbstractCosineScore):
  spectra1 = models.ForeignKey(
    'Spectra',
    related_name='spectra1',
    on_delete=models.CASCADE)
  spectra2 = models.ForeignKey(
    'Spectra',
    related_name='spectra2',
    on_delete=models.CASCADE)
  # ~ score = models.DecimalField(
    # ~ max_digits=10, decimal_places=6, blank=False)

class SearchSpectraCosineScore(AbstractCosineScore):
  spectra1 = models.ForeignKey(
    'SearchSpectra',
    related_name='search_spectra1',
    on_delete=models.CASCADE)
  spectra2 = models.ForeignKey(
    'Spectra',
    related_name='search_spectra2',
    on_delete=models.CASCADE)
    
class AbstractSpectra(models.Model):
  # ~ privacy_level = models.ForeignKey(
    # ~ 'PrivacyLevel',
    # ~ on_delete=models.CASCADE,
    # ~ blank=True)
  PUBLIC = 'PB'
  PRIVATE = 'PR'
  privacyChoices = [
    (PUBLIC, 'Public'),
    (PRIVATE, 'Private'),
  ]
  privacy_level = models.CharField(
    max_length=2,
    choices=privacyChoices,
    default=PUBLIC,
    blank=True,
    null=True
  )
  
  library = models.ForeignKey(
    'Library',
    on_delete=models.CASCADE,
    blank=True,
    null=True)
  
  created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    # ~ related_name='created_by',
    on_delete=models.CASCADE,
    blank=True,
    null=True)
  
  lab_name = models.ForeignKey(
    'LabGroup',
    on_delete=models.CASCADE,
    blank=True,
    null=True)
  
  # Averaged m/z and intensity values in case of collapse spectra
  # ~ peak_matrix = models.TextField(blank=True)
  # ~ spectrum_intensity = models.TextField(blank=True)
  
  peak_mass = models.TextField(blank=True,
    help_text = 'A list of comma separated values, e.g., "1,2,3"')
  peak_intensity = models.TextField(blank=True,
    help_text = 'A list of comma separated values, e.g., "1,2,3"')
  peak_snr = models.TextField(blank=True,
    help_text = 'A list of comma separated values, e.g., "1,2,3"')
  
  spectrum_mass_hash = models.CharField(max_length=255, blank=True)
  spectrum_intensity_hash = models.CharField(max_length=255, blank=True)
  
  # ~ xml_hash = models.TextField(blank=True)
  xml_hash = models.ForeignKey(
    'XML',
    #### related_name='uploaded_by',
    db_column='xml_hash',
    on_delete=models.CASCADE, 
    blank=True,
    null=True)
    
  # ~ strain_id = models.TextField(blank=True)
  strain_id = models.ForeignKey(
    'Metadata',
    #### related_name='has_metadata',
    db_column='strain_id',
    on_delete=models.CASCADE,
    blank=True,
    null=True)
  
  # ~ unique_together = (
    # ~ strain_id,
    # ~ spectrum_mass_hash,
    # ~ spectrum_intensity_hash
  # ~ )
  
  class Meta:                                                                 
    abstract = True                                                         
  
  def get_absolute_url(self):
    return reverse('chat:view_spectra', args=(self.id,))
  
class CollapsedSpectra(AbstractSpectra):
  # e.g., cs.spectra.add(s1, s2, ..., sN)
  collapsed_spectra = models.ManyToManyField('Spectra')
  
  peak_percent_presence = models.DecimalField( # e.g. 70.00%
    max_digits=4, decimal_places=2, blank=False)
  lower_mass_cutoff = models.IntegerField(blank=True) #e.g. 0
  upper_mass_cutoff = models.IntegerField(blank=True) #e.g. 6000
  min_SNR = models.DecimalField(
    max_digits=4, decimal_places=2, blank=False) #e.g. 0-1???
  tolerance = models.DecimalField(
    max_digits=10, decimal_places=6, blank=False, default=0.002) #default = 0.002,
  
  # spectra is protein(>6k) OR small molecule(<6k),
  # aka tofMode or acquisitionOperatorMode (REFLECTOR/LINEAR)
  # spectraContent is "protein" in R function.
  PROTEIN = 'PR'
  SM = 'SM'
  spectraChoices = [
    (PROTEIN, 'Protein'),
    (SM, 'Small Molecule'),
  ]
  spectra_content = models.CharField(
    max_length=2,
    choices=spectraChoices,
    default=PROTEIN,
  )
  
  generated_date = models.DateTimeField(auto_now_add=True, blank=True)


class PrivacyLevel(models.Model):
  """ Privacy level for library, spectra, etc.
  """
  PUBLIC = 'PB'
  PRIVATE = 'PR'
  privacyChoices = [
    (PUBLIC, 'Public'),
    (PRIVATE, 'Private'),
  ]
  level = models.CharField(
    max_length=2,
    choices=privacyChoices,
    default=PUBLIC,
  )
  
class Library(models.Model):
  """
  """
  created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    # ~ related_name='created_by',
    on_delete=models.CASCADE)
  
  lab_name = models.ForeignKey('LabGroup', on_delete=models.CASCADE)
  
  title = models.CharField(max_length=200)
  description = models.TextField(blank=True)
  
  PUBLIC = 'PB'
  PRIVATE = 'PR'
  privacyChoices = [
    (PUBLIC, 'Public'),
    (PRIVATE, 'Private'),
  ]
  privacy_level = models.CharField(
    max_length=2,
    choices=privacyChoices,
    default=PUBLIC,
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
    max_length=2,
    choices=qualChoices,
    default=BRONZE,
  )
  
  def __str__(self):
    #return f"{self.user.username}'s library"
    return self.title
  
  def get_fields(self):
    return [(field.verbose_name, field.value_to_string(self)) for field in Library._meta.fields]
  
  def get_absolute_url(self):
    return reverse('chat:view_library', args=(self.id,))
      
class LabGroup(models.Model):
  '''At least one owner. Zero or more members.'''
  lab_name = models.CharField(max_length=200)
  lab_description = models.TextField(blank=True)
  owners = models.ManyToManyField(settings.AUTH_USER_MODEL)
  members = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="lab_members")
  
    #models.ForeignKey(
    #settings.AUTH_USER_MODEL,
    #on_delete = models.CASCADE)
  
  def __str__(self):
    return self.lab_name
  
  def get_fields(self):
    return [(field.verbose_name, field.value_to_string(self)) for field in LabGroup._meta.fields]
    
  def get_absolute_url(self):
    return reverse('chat:view_lab', args=(self.id,))

from django.db.models.signals import post_save
from django.dispatch import receiver
#import accounts.models as m
@receiver(post_save, sender=LabGroup, dispatch_uid=None)
def update_stock(sender, instance, **kwargs):
  '''Add each owner to the group as a member when creating the group.
  TODO: This only adds the owners when the LabGroup is first created.
        When updating the lab group, the form's values override this.'''
  for owner in instance.owners.all():
    instance.members.add(owner)
    #instance.members.add(m.User.objects.get(username=str(owner)))
  post_save.disconnect(update_stock, sender=LabGroup)
  instance.save()
  post_save.connect(update_stock, sender=LabGroup)
 
class SearchSpectra(AbstractSpectra):
  peak_mass = models.TextField(blank=True)
  peak_intensity = models.TextField(blank=True)
  peak_snr = models.TextField(blank=True)
  created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    # ~ related_name='created_by',
    on_delete=models.CASCADE,
    blank=True,
    null=True)
  
class Spectra(AbstractSpectra):
  """ Spectra Model
  -- Sqlite NUMERIC data type: 'Type affinity is the recommended type
  of data stored in a column. However, you still can store any type of
  data as you wish, these types are recommended not required.'
  -- DecimalField: Using parameters max_digits=30, decimal_places=20
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
  """
  
  
  # UNIQUE(strain_id, spectrum_mass_hash, spectrum_intensity_hash) 
  
  
  # Each spectra belongs to one library.
  # Each library contains many spectra.
  # ~ library = models.ForeignKey('Library', on_delete=models.CASCADE)
  
  # ~ created_by = models.ForeignKey(
    # ~ settings.AUTH_USER_MODEL,
    ###related_name='uploaded_by',
    # ~ on_delete=models.CASCADE)
  
  # ~ privacy_level = models.ForeignKey(
    # ~ 'PrivacyLevel',
    # ~ on_delete=models.CASCADE,
    # ~ blank=True)
    
  picture = models.ImageField(upload_to='spectra_images', blank=True)
  description = models.TextField(max_length=2048, blank=True)
  posted_date = models.DateTimeField(auto_now_add=True, blank=True)
  
  max_mass = models.IntegerField(blank=True)
  min_mass = models.IntegerField(blank=True)
  ignore = models.IntegerField(blank=True)
  number = models.IntegerField(blank=True)  
  time_delay = models.IntegerField(blank=True)
  time_delta = models.DecimalField(max_digits=30, decimal_places=20, blank=True)
  calibration_constants = models.TextField(blank=True)
  v1_tof_calibration = models.TextField(blank=True)
  data_type = models.CharField(max_length=255, blank=True)
  data_system = models.CharField(max_length=255, blank=True)
  spectrometer_type = models.CharField(max_length=255, blank=True)
  inlet = models.CharField(max_length=255, blank=True)
  ionization_mode = models.CharField(max_length=255, blank=True)
  acquisition_method = models.CharField(max_length=255, blank=True)
  # ~ acquisition_date = models.DateTimeField(auto_now_add=False)
  acquisition_date = models.CharField(max_length=255, blank=True)
  acquisition_mode = models.CharField(max_length=255, blank=True)
  tof_mode = models.CharField(max_length=255, blank=True)
  acquisition_operator_mode = models.CharField(max_length=255, blank=True)
  laser_attenuation = models.IntegerField(blank=True)
  digitizer_type = models.CharField(max_length=255, blank=True)
  flex_control_version = models.CharField(max_length=255, blank=True)
  cId = models.CharField(max_length=255, blank=True) # appears to be a key to another table ???
  instrument = models.CharField(max_length=255, blank=True)
  instrument_id = models.CharField(max_length=255, blank=True)
  instrument_type = models.CharField(max_length=255, blank=True)
  mass_error = models.DecimalField(max_digits=30, decimal_places=20, blank=True)
  laser_shots = models.IntegerField(blank=True)
  patch = models.CharField(max_length=255, blank=True)
  path = models.CharField(max_length=255, blank=True)
  laser_repetition = models.DecimalField(max_digits=20, decimal_places=6, blank=True)
  spot = models.CharField(max_length=255, blank=True)
  spectrum_type = models.CharField(max_length=255, blank=True)
  target_count = models.DecimalField(max_digits=10, decimal_places=4, blank=True)
  target_id_string = models.CharField(max_length=255, blank=True)
  target_serial_number = models.CharField(max_length=255, blank=True)
  target_type_number = models.CharField(max_length=255, blank=True)
  
  
    
  # Peaks/Intens.
  # In the format of comma-separated fields: "peak1,peak2,...,peakN"
  
  #peaks = models.TextField(blank=True)
  #intensities = models.TextField(blank=True)
  #testField = models.TextField(blank=True)
  #spectraID = models.CharField(
  #  max_length=100, blank=True, unique=True, default=uuid.uuid4)
  
  # Todo
  # foreign key to Metadata?
  #strain_id = models.TextField(blank=True)
  # Todo
  # foreign key to XML?
  #xml_hash = models.TextField(blank=True) 
  
  def __str__(self):
    return f"{self.created_by.username}'s spectra"
  
  def get_fields(self):
    return [(field.verbose_name, field.value_to_string(self)) for field in Spectra._meta.fields]
  
class Metadata(models.Model):
  ''' UNIQUE(strain_id).
  -- Removing unique from strain_id ???
  '''
  # ~ strain_id = models.TextField(blank=True)
  strain_id = models.CharField(max_length=200, blank=True) #, unique=True)
  genbank_accession = models.CharField(max_length=200, blank=True)
  ncbi_taxid = models.CharField(max_length=200, blank=True)
  cKingdom = models.CharField(max_length=200, blank=True)
  cPhylum = models.CharField(max_length=200, blank=True)
  cClass = models.CharField(max_length=200, blank=True)
  cOrder = models.CharField(max_length=200, blank=True)
  cGenus = models.CharField(max_length=200, blank=True)
  cSpecies = models.CharField(max_length=200, blank=True)
  maldi_matrix = models.TextField(blank=True)
  dsm_cultivation_media = models.TextField(blank=True)
  cultivation_temp_celsius = models.TextField(blank=True)
  cultivation_time_days = models.TextField(blank=True)
  cultivation_other = models.TextField(blank=True)
  
  user_firstname_lastname = models.CharField(max_length=200, blank=True)
  user_orcid = models.CharField(max_length=200, blank=True)
  pi_firstname_lastname = models.CharField(max_length=200, blank=True)
  pi_orcid = models.CharField(max_length=200, blank=True)
  
  dna_16s = models.TextField(blank=True)
  
  created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    blank=True,
    null=True)
  
  lab_name = models.ForeignKey(
    'LabGroup',
    on_delete=models.CASCADE,
    blank=True,
    null=True)
    
  def get_fields(self):
    return [(field.verbose_name, field.value_to_string(self)) for field in Metadata._meta.fields]
  
  def __str__(self):
    #return f"{self.user.username}'s library"
    return self.strain_id
    
class XML(models.Model):
  '''UNIQUE(xml_hash) ---- removed '''
  xml_hash = models.TextField(blank=True) #, unique=True
  # ~ xml             BLOB,
  #########################
  xml = models.TextField(blank=True)
  
  manufacturer = models.CharField(max_length=200, blank=True)
  model = models.CharField(max_length=200, blank=True)
  
  ionization = models.TextField(blank=True)
  analyzer = models.TextField(blank=True)
  detector = models.TextField(blank=True)
  # ~ instrument_metafile BLOB,
  #############################
  instrument_metafile = models.TextField(blank=True)
  
  created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    blank=True,
    null=True)
  
  lab_name = models.ForeignKey(
    'LabGroup',
    on_delete=models.CASCADE,
    blank=True,
    null=True)
  
  def get_fields(self):
    return [(field.verbose_name, field.value_to_string(self)) for field in XML._meta.fields]
  
  def get_absolute_url(self):
    return reverse('chat:view_xml', args=(self.xml_hash,))
  
  def __str__(self):
    #return f"{self.user.username}'s library"
    return self.xml_hash
    
class Version(models.Model):
  idbac_version = models.CharField(max_length=200, blank=True)
  r_version = models.TextField(blank=True)
  db_version = models.CharField(max_length=200, blank=True)
  
  def get_fields(self):
    return [(field.verbose_name, field.value_to_string(self)) for field in Version._meta.fields]
    
class Locale(models.Model):
  locale = models.TextField(blank=True)
  
  def get_fields(self):
    return [(field.verbose_name, field.value_to_string(self)) for field in Locale._meta.fields]
    
class Comment(models.Model):
  """ The comments Models """

  user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comments', on_delete=models.CASCADE)
  spectra = models.ForeignKey(Spectra, related_name='comments', on_delete=models.CASCADE)
  text = models.TextField(max_length=2048, blank=True)
  comment_date = models.DateTimeField(auto_now_add=True)

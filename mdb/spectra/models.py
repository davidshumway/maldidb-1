from django.db import models
from django.urls import reverse
from chat.models import *

class AbstractSpectra(models.Model):
  '''
  '''
  
  # Privacy level is library-wide
  # ~ privacyChoices = [
    # ~ ('PB', 'Public'),
    # ~ ('PR', 'Private'),
  # ~ ]
  # ~ privacy_level = models.CharField(
    # ~ max_length = 2,
    # ~ choices = privacyChoices,
    # ~ default = 'PB',
    # ~ blank = True,
    # ~ null = True
  # ~ )
  
  library = models.ForeignKey(
    'chat.Library',
    on_delete = models.CASCADE,
    blank = True,
    null = True)
  
  created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    # ~ related_name = 'created_by',
    on_delete = models.CASCADE,
    blank = True,
    null = True)
  
  # ~ lab = models.ForeignKey(
    # ~ 'chat.LabGroup',
    # ~ on_delete = models.CASCADE,
    # ~ blank = True,
    # ~ null = True)
  
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
    'chat.XML',
    db_column = 'xml_hash',
    on_delete = models.CASCADE, 
    blank = True,
    null = True)
    
  strain_id = models.ForeignKey(
    'chat.Metadata',
    db_column = 'strain_id',
    on_delete = models.CASCADE,
    blank = True,
    null = True,
    db_index=True) # sort by sid
  
  # ~ unique_together = (
    # ~ strain_id,
    # ~ spectrum_mass_hash,
    # ~ spectrum_intensity_hash
  # ~ )
  
  class Meta:
    abstract = True
    unique_together= (
      ('spectrum_mass_hash', 'spectrum_intensity_hash', 'library'),)
    # ~ unique_together= (('xml_hash', 'library'),)
  
  def get_absolute_url(self):
    return reverse('spectra:view_spectra', args = (self.id,))
  
class CollapsedSpectra(AbstractSpectra):
  '''
  -- Inherits strain_id
  -- Pipeline cols: peak_percent_presence, lower_mass_cutoff,
    upper_mass_cutoff, min_snr, tolerance
  -- Remove lower and upper mass cutoff.
  -- MALDIQuant docs: 4.10 Feature Matrix: We choose a very low
    signal-to-noise ratio to keep as much features as possible.
    To remove some false positive peaks we remove less frequent peaks.
  '''
  # e.g., collapsed_spectra.add(s1, s2, ..., sN)
  collapsed_spectra = models.ManyToManyField('Spectra')
  
  peak_percent_presence = models.DecimalField( # e.g. 70.00%
    max_digits = 4, decimal_places = 1, blank = False, default = 70.0)
  # ~ lower_mass_cutoff = models.IntegerField(blank = True) #e.g. 0
  # ~ upper_mass_cutoff = models.IntegerField(blank = True) #e.g. 6000
  max_mass = models.IntegerField(blank = True, null = True)
  min_mass = models.IntegerField(blank = True, null = True)
  
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
  
  # ~ class Meta:
    # ~ indexes = [
      # ~ models.Index(fields = ['collapsed_spectra',]),
    # ~ ]
    
  def get_absolute_url(self):
    return reverse('spectra:view_spectra2', kwargs = {'spectra_id' : self.id})
  
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
    return f"id:{self.id} spot:{self.spot} strain_id:{self.strain_id}"
    # ~ if self.created_by != None:
      # ~ return f"{self.created_by.username}"
    # ~ else: return 'Created by an anonymous user'
  
  def get_fields(self):
    return [(field.verbose_name, field.value_to_string(self)) for field in Spectra._meta.fields]
  
class AbstractCosineScore(models.Model):
  score = models.DecimalField(
    max_digits = 10, decimal_places = 6, blank = False)
    
  class Meta:
    abstract = True

class BinnedPeaks(models.Model):
  '''
  Binned peaks version of a spectra when matched against set of spectra.
  '''
  peak_mass = models.TextField(blank = True)
  peak_snr = models.TextField(blank = True)
  spectra = models.ForeignKey(
    'CollapsedSpectra',
    on_delete = models.CASCADE)
  
# ~ class CollapsedCosineScore(AbstractCosineScore):
class CollapsedCosineScore(models.Model):
  '''
  '''
  spectra = models.ForeignKey(
    'CollapsedSpectra',
    on_delete = models.CASCADE)
  library = models.ForeignKey(
    'chat.Library',
    on_delete = models.CASCADE)
  result = models.TextField()
  # ~ scores = models.TextField()
  # ~ spectra_ids = models.TextField()
  #intensities = models.TextField()
  #binned_peaks = models.ManyToManyField('BinnedPeaks')
  
  # ~ class Meta:
    # ~ indexes = [
      # ~ models.Index(fields = ['spectra', 'library']),
    # ~ ]
# ~ class CollapsedCosineScore(AbstractCosineScore):
  # ~ spectra1 = models.ForeignKey(
    # ~ 'CollapsedSpectra',
    # ~ related_name = 'spectra1',
    # ~ on_delete = models.CASCADE)
  # ~ spectra2 = models.ForeignKey(
    # ~ 'CollapsedSpectra',
    # ~ related_name = 'spectra2',
    # ~ on_delete = models.CASCADE)
      
class SpectraCosineScore(AbstractCosineScore):
  spectra1 = models.ForeignKey(
    'Spectra',
    related_name = 'spectra1',
    on_delete = models.CASCADE)
  spectra2 = models.ForeignKey(
    'Spectra',
    related_name = 'spectra2',
    on_delete = models.CASCADE)

class SearchSpectraCosineScore(AbstractCosineScore):
  spectra1 = models.ForeignKey(
    'SearchSpectra',
    related_name = 'search_spectra1',
    on_delete = models.CASCADE)
  spectra2 = models.ForeignKey(
    'Spectra',
    related_name = 'search_spectra2',
    on_delete = models.CASCADE)

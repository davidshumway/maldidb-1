from django.db import models
from django.conf import settings
import uuid


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
		
class SpectraCosineScore(AbstractCosineScore):
	spectra1 = models.ForeignKey(
		'Spectra',
		related_name='spectra1',
		on_delete=models.CASCADE)
	spectra2 = models.ForeignKey(
		'Spectra',
		related_name='spectra2',
		on_delete=models.CASCADE)
	

class AbstractSpectra(models.Model):
	privacy_level = models.ForeignKey(
		'PrivacyLevel',
		on_delete=models.CASCADE,
		blank=True)
	library = models.ForeignKey('Library', on_delete=models.CASCADE)
	created_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		# ~ related_name='created_by',
		on_delete=models.CASCADE)
	# Averaged m/z and intensity values in case of collapse spectra
	peak_matrix = models.TextField(blank=True)
	spectrum_intensity = models.TextField(blank=True)
	
	
	
	spectrum_mass_hash = models.TextField(blank=True)
	spectrum_intensity_hash = models.TextField(blank=True)
	
	# ~ xml_hash = models.TextField(blank=True)
	xml_hash = models.ForeignKey(
		'XML',
		# ~ related_name='uploaded_by',
		db_column='xml_hash',
		on_delete=models.CASCADE)
		
	# ~ strain_id = models.TextField(blank=True)
	strain_id = models.ForeignKey(
		'Metadata',
		# ~ related_name='has_metadata',
		db_column='strain_id',
		on_delete=models.CASCADE,
		blank=True)
		
		# ~ peak_matrix                           BLOB,
	#inherits
	# ~ peak_matrix = models.TextField(blank=True)
		# ~ spectrum_intensity                    BLOB,
	#inherits
	# ~ spectrum_intensity = models.TextField(blank=True)
		# ~ max_mass                              INTEGER,
	
	
	
	unique_together = (
		strain_id,
		spectrum_mass_hash,
		spectrum_intensity_hash
	) 
	
	
	
	
	
	
	class Meta:                                                                 
		abstract = True                                                         

	
# ~ class CollapsedSpectra(models.Model):
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
	# Date when created
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
		
	title = models.TextField(max_length=2048, blank=True)
	
	privacy_level = models.ForeignKey(
		'PrivacyLevel',
		on_delete=models.CASCADE,
		blank=True)
	#id = models.AutoField()
	
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
		
class LabGroup(models.Model):
	lab_name = models.TextField()
	
	def __str__(self):
		return self.lab_name
	
	def get_fields(self):
		return [(field.verbose_name, field.value_to_string(self)) for field in LabGroup._meta.fields]
		
class Spectra(AbstractSpectra):
	""" Spectra Model
	-- Sqlite NUMERIC data type: 'Type affinity is the recommended type
	of data stored in a column. However, you still can store any type of
	data as you wish, these types are recommended not required.'
	-- DecimalField: Using parameters max_digits=30, decimal_places=20
	-- IntegerField: -2147483648 to 2147483647
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
		
	picture = models.ImageField(upload_to='spectra', blank=True)
	text = models.TextField(max_length=2048, blank=True)
	posted_date = models.DateTimeField(auto_now_add=True, blank=True)
	
	
	number = models.IntegerField(blank=True)
		# ~ time_delay                            INTEGER,
	time_delay = models.IntegerField(blank=True)
		# ~ time_delta                            NUMERIC,
	time_delta = models.DecimalField(max_digits=30, decimal_places=20, blank=True)
	calibration_constants = models.TextField(blank=True)
	v1_tof_calibration = models.TextField(blank=True)
	data_type = models.TextField(blank=True)
	data_system = models.TextField(blank=True)
	spectrometer_type = models.TextField(blank=True)
	inlet = models.TextField(blank=True)
	ionization_mode = models.TextField(blank=True)
	acquisition_method = models.TextField(blank=True)
	acquisition_date = models.TextField(blank=True)
	acquisition_mode = models.TextField(blank=True)
	tof_mode = models.TextField(blank=True)
	acquisition_operator_mode = models.TextField(blank=True)
		# ~ laser_attenuation                     INTEGER,
	laser_attenuation = models.IntegerField(blank=True)
	digitizer_type = models.TextField(blank=True)
	flex_control_version = models.TextField(blank=True)
	# Original name is "id"
	cId = models.TextField(blank=True)
	instrument = models.TextField(blank=True)
	instrument_id = models.TextField(blank=True)
	instrument_type = models.TextField(blank=True)
		# ~ mass_error                            NUMERIC,
	mass_error = models.DecimalField(max_digits=30, decimal_places=20, blank=True)
		# ~ laser_shots                           INTEGER,
	laser_shots = models.IntegerField(blank=True)
	patch = models.TextField(blank=True)
	path = models.TextField(blank=True)
	laser_repetition = models.TextField(blank=True)
	spot = models.TextField(blank=True)
	spectrum_type = models.TextField(blank=True)
	target_count = models.TextField(blank=True)
	target_id_string = models.TextField(blank=True)
	target_serial_number = models.TextField(blank=True)
	target_type_number = models.TextField(blank=True)
	max_mass = models.IntegerField(blank=True)
		# ~ min_mass                              INTEGER,
	min_mass = models.IntegerField(blank=True)
		# ~ ignore                               INTEGER,
	ignore = models.IntegerField(blank=True)
		# ~ number                               INTEGER,
		
		
	# Peaks/Intens.
	# In the format of comma-separated fields: "peak1,peak2,...,peakN"
	
	#peaks = models.TextField(blank=True)
	#intensities = models.TextField(blank=True)
	#testField = models.TextField(blank=True)
	#spectraID = models.CharField(
	#	max_length=100, blank=True, unique=True, default=uuid.uuid4)
	
	
	
	def __str__(self):
		return f"{self.user.username}'s spectra"
	
	def get_fields(self):
		return [(field.verbose_name, field.value_to_string(self)) for field in Spectra._meta.fields]
	
class Metadata(models.Model):
	''' UNIQUE(strain_id).
	-- Removing unique from strain_id ???
	'''
	# ~ strain_id = models.TextField(blank=True)
	strain_id = models.TextField(blank=True, unique=True)
	genbank_accession = models.TextField(blank=True)
	ncbi_taxid = models.TextField(blank=True)
	cKingdom = models.TextField(blank=True)
	cPhylum = models.TextField(blank=True)
	cClass = models.TextField(blank=True)
	cOrder = models.TextField(blank=True)
	cGenus = models.TextField(blank=True)
	cSpecies = models.TextField(blank=True)
	maldi_matrix = models.TextField(blank=True)
	dsm_cultivation_media = models.TextField(blank=True)
	cultivation_temp_celsius = models.TextField(blank=True)
	cultivation_time_days = models.TextField(blank=True)
	cultivation_other = models.TextField(blank=True)
	user_firstname_lastname = models.TextField(blank=True)
	user_orcid = models.TextField(blank=True)
	pi_firstname_lastname = models.TextField(blank=True)
	pi_orcid = models.TextField(blank=True)
	dna_16s = models.TextField(blank=True)
	
	def get_fields(self):
		return [(field.verbose_name, field.value_to_string(self)) for field in Metadata._meta.fields]
		
class XML(models.Model):
	'''UNIQUE(xml_hash) ---- removed '''
	xml_hash = models.TextField(blank=True) #, unique=True
	# ~ xml             BLOB,
	#########################
	xml = models.TextField(blank=True)
	manufacturer = models.TextField(blank=True)
	model = models.TextField(blank=True)
	ionization = models.TextField(blank=True)
	analyzer = models.TextField(blank=True)
	detector = models.TextField(blank=True)
	# ~ instrument_metafile BLOB,
	#############################
	instrument_metafile = models.TextField(blank=True)
	
	def get_fields(self):
		return [(field.verbose_name, field.value_to_string(self)) for field in XML._meta.fields]
    
class Version(models.Model):
	idbac_version = models.TextField(blank=False)
	r_version = models.TextField(blank=False)
	db_version = models.TextField(blank=False)
	
	def get_fields(self):
		return [(field.verbose_name, field.value_to_string(self)) for field in Version._meta.fields]
		
class Locale(models.Model):
	locale = models.TextField(blank=False)
	
	def get_fields(self):
		return [(field.verbose_name, field.value_to_string(self)) for field in Locale._meta.fields]
		
class Comment(models.Model):
	""" The comments Models """

	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comments', on_delete=models.CASCADE)
	spectra = models.ForeignKey(Spectra, related_name='comments', on_delete=models.CASCADE)
	text = models.TextField(max_length=2048, blank=True)
	comment_date = models.DateTimeField(auto_now_add=True)

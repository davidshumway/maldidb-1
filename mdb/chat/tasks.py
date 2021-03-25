# ~ from celery import Celery

# ~ from . import forms
# ~ from . import models

# ~ from .forms import SpectraForm, MetadataForm, \
  # ~ LoadSqliteForm, XmlForm, LocaleForm, VersionForm, AddLibraryForm, \
  # ~ AddLabGroupForm, AddXmlForm, LabProfileForm, SearchForm, \
  # ~ ViewCosineForm, SpectraSearchForm, LibraryCollapseForm

# ~ from .models import Spectra, SearchSpectra, SpectraCosineScore, \
  # ~ SearchSpectraCosineScore, Metadata, XML, Locale, Version, Library, \
  # ~ LabGroup

# ~ app = Celery('tasks', broker='pyamqp://guest@localhost//')
  
# ~ @app.task
# ~ def add(x, y):
  # ~ return x + y
  
# ~ @app.task
# ~ def add_sqlite_async(request, tmpForm):
  # ~ import json
  # ~ import sqlite3
  
  # ~ if request.FILES and request.FILES['file']:
    # ~ f = request.FILES['file']
    # ~ with open('/tmp/test.db', 'wb+') as destination:
      # ~ for chunk in f.chunks():
        # ~ destination.write(chunk)
    # ~ connection = sqlite3.connect('/tmp/test.db')
    # ~ idbac_sqlite_insert(request, tmpForm, connection)
  # ~ elif tmpForm.cleaned_data['upload_type'] == 'all': # hosted on server
    # ~ hc = [
      # ~ '2019_04_15_10745_db-2_0_0.sqlite',
      # ~ '2019_07_02_22910_db-2_0_0.sqlite',
      # ~ '2019_09_11_1003534_db-2_0_0.sqlite',
      # ~ '2019_10_10_1003534_db-2_0_0.sqlite',
      # ~ '2019_06_06_22910_db-2_0_0.sqlite',
      # ~ '2019_06_06_22910_db-2_0_0.sqlite',
      # ~ '2019_09_18_22910_db-2_0_0.sqlite',
      # ~ '2019_11_13_1003534_db-2_0_0.sqlite',
      # ~ '2019_06_12_10745_db-2_0_0.sqlite',
      # ~ '2019_09_04_10745_db-2_0_0.sqlite',
      # ~ '2019_09_25_10745_db-2_0_0.sqlite',
      # ~ '2019_11_20_1003534_db-2_0_0.sqlite',
    # ~ ]
    # ~ for f in hc:
      # ~ connection = sqlite3.connect('/home/ubuntu/' + f)
      # ~ idbac_sqlite_insert(request, tmpForm, connection)    
  
# ~ def idbac_sqlite_insert(request, tmpForm, connection):
    
  # ~ cursor = connection.cursor()
  
  # ~ # Metadata
  # ~ rows = cursor.execute("SELECT * FROM metaData").fetchall()
  # ~ for row in rows:
    # ~ data = {
      # ~ 'strain_id': row[0],
      # ~ 'genbank_accession': row[1],
      # ~ 'ncbi_taxid': row[2],
      # ~ 'cKingdom': row[3],
      # ~ 'cPhylum': row[4],
      # ~ 'cClass': row[5],
      # ~ 'cOrder': row[6],
      # ~ 'cGenus': row[7],
      # ~ 'cSpecies': row[8],
      # ~ 'maldi_matrix': row[9],
      # ~ 'dsm_cultivation_media': row[10],
      # ~ 'cultivation_temp_celsius': row[11],
      # ~ 'cultivation_time_days': row[12],
      # ~ 'cultivation_other': row[13],
      # ~ 'user_firstname_lastname': row[14],
      # ~ 'user_orcid': row[15],
      # ~ 'pi_firstname_lastname': row[16],
      # ~ 'pi_orcid': row[17],
      # ~ 'dna_16s': row[18],
      
      # ~ 'created_by': request.user.id,
      # ~ 'library': tmpForm.cleaned_data['library'][0].id,
      # ~ 'lab_name': tmpForm.cleaned_data['lab_name'][0].id,
    # ~ }
    # ~ form = MetadataForm(data)
    # ~ if form.is_valid():
      # ~ entry = form.save(commit=False)
      # ~ entry.save()
    # ~ else:
      # ~ print(form.errors)
      # ~ raise ValueError('xxxxx')
  
  # ~ # XML
  # ~ rows = cursor.execute("SELECT * FROM XML").fetchall()
  # ~ for row in rows:
    # ~ data = {
      # ~ 'xml_hash': row[0],
      # ~ 'xml': row[1],
      # ~ 'manufacturer': row[2],
      # ~ 'model': row[3],
      # ~ 'ionization': row[4],
      # ~ 'analyzer': row[5],
      # ~ 'detector': row[6],
      # ~ 'instrument_metafile': row[7],
      # ~ 'created_by': request.user.id,
      # ~ 'library': tmpForm.cleaned_data['library'][0].id,
      # ~ 'lab_name': tmpForm.cleaned_data['lab_name'][0].id,
    # ~ }
    # ~ form = XmlForm(data)
    # ~ if form.is_valid():
      # ~ entry = form.save(commit=False)
      # ~ entry.save()
    # ~ else:
      # ~ form.non_field_errors()
      # ~ field_errors = [ (field.label, field.errors) for field in form ] 
      # ~ raise ValueError('xxxxx')
  
  # ~ # Version
  # ~ rows = cursor.execute("SELECT * FROM version").fetchall()
  # ~ for row in rows:
    # ~ data = {
      # ~ 'idbac_version': row[0],
      # ~ 'r_version': row[1],
      # ~ 'db_version': row[2],
    # ~ }
    # ~ form = VersionForm(data)
    # ~ if form.is_valid():
      # ~ entry = form.save(commit=False)
      # ~ entry.save()
    # ~ else:
      # ~ raise ValueError('xxxxx')
  
  # ~ # Locale
  # ~ rows = cursor.execute("SELECT * FROM locale").fetchall()
  # ~ for row in rows:
    # ~ data = {
      # ~ 'locale': row[0],
    # ~ }
    # ~ form = LocaleForm(data)
    # ~ if form.is_valid():
      # ~ entry = form.save(commit=False)
      # ~ entry.save()
    # ~ else:
      # ~ raise ValueError('xxxxx')
    
  
  # ~ # Spectra
  # ~ rows = cursor.execute("SELECT * FROM spectra").fetchall()
  # ~ for row in rows:
    
    # ~ sxml = XML.objects.filter(xml_hash=row[2])
    # ~ if sxml:
      # ~ sxml = sxml[0]
    # ~ smd = Metadata.objects.filter(strain_id=row[3])
    # ~ if smd:
      # ~ smd = smd[0]
    
    # ~ pm = json.loads(row[4])

    # ~ data = {
      # ~ 'created_by': request.user.id,
      # ~ 'library': tmpForm.cleaned_data['library'][0].id,
      # ~ 'lab_name': tmpForm.cleaned_data['lab_name'][0].id,
      
      # ~ 'privacy_level': tmpForm.cleaned_data['privacy_level'][0],
      
      # ~ 'spectrum_mass_hash': row[0],
      # ~ 'spectrum_intensity_hash': row[1],
      
      # ~ 'xml_hash': sxml.id,
      # ~ 'strain_id': smd.id,
      
      # ~ 'peak_mass': ",".join(map(str, pm['mass'])),
      # ~ 'peak_intensity': ",".join(map(str, pm['intensity'])),
      # ~ 'peak_snr': ",".join(map(str, pm['snr'])),
      
      # ~ 'max_mass': row[6],
      # ~ 'min_mass': row[7],
      # ~ 'ignore': row[8],
      # ~ 'number': row[9],
      # ~ 'time_delay': row[10],
      # ~ 'time_delta': row[11],
      # ~ 'calibration_constants': row[12],
      # ~ 'v1_tof_calibration': row[13],
      # ~ 'data_type': row[14],
      # ~ 'data_system': row[15],
      # ~ 'spectrometer_type': row[16],
      # ~ 'inlet': row[17],
      # ~ 'ionization_mode': row[18],
      # ~ 'acquisition_method': row[19],
      # ~ 'acquisition_date': row[20],
      # ~ 'acquisition_mode': row[21],
      # ~ 'tof_mode': row[22],
      # ~ 'acquisition_operator_mode': row[23],
      # ~ 'laser_attenuation': row[24],
      # ~ 'digitizer_type': row[25],
      # ~ 'flex_control_version': row[26],
      # ~ 'cId': row[27],
      # ~ 'instrument': row[28],
      # ~ 'instrument_id': row[29],
      # ~ 'instrument_type': row[30],
      # ~ 'mass_error': row[31],
      # ~ 'laser_shots': row[32],
      # ~ 'patch': row[33],
      # ~ 'path': row[34],
      # ~ 'laser_repetition': row[35],
      # ~ 'spot': row[36],
      # ~ 'spectrum_type': row[37],
      # ~ 'target_count': row[38],
      # ~ 'target_id_string': row[39],
      # ~ 'target_serial_number': row[40],
      # ~ 'target_type_number': row[41],
    # ~ }
    # ~ form = SpectraForm(data)
    # ~ if form.is_valid():
      # ~ entry = form.save(commit=False)
      # ~ entry.save()
    # ~ else:
      # ~ form.non_field_errors()
      # ~ field_errors = [ (field.label, field.errors) for field in form ] 
      # ~ raise ValueError('xxxxx')
  
  
  
# ~ from celery import shared_task
# ~ from celery_progress.backend import ProgressRecorder
# ~ import time

# ~ @shared_task(bind=True)
# ~ def ProcessDownload(self):
	# ~ print('Task started')
	# ~ progress_recorder = ProgressRecorder(self)
	# ~ print('Start')
	# ~ for i in range(5):
		# ~ time.sleep(1)
		# ~ print(i + 1)
		# ~ progress_recorder.set_progress(i + 1, 5, description="Downloading")
	# ~ print('End')
	# ~ return 'Task Complete'
  
  
  
  
# ~ from celery import shared_task
# ~ from celery_progress.backend import ProgressRecorder
# ~ import time

# ~ @shared_task(bind=True)
# ~ def my_task(self, seconds):
  # ~ progress_recorder = ProgressRecorder(self)
  # ~ result = 0
  # ~ for i in range(seconds):
    # ~ time.sleep(1)
    # ~ result += i
    ##progress_recorder.set_progress(i + 1, seconds)
    # ~ progress_recorder.set_progress(i + 1, seconds,
      # ~ description = 'my progress description'
    # ~ )
  # ~ return result

from django.shortcuts import redirect, render
from .forms import LoadSqliteForm
from chat.forms import *
from spectra.forms import SpectraForm
from chat.models import Spectra, SearchSpectra, SpectraCosineScore, \
  SearchSpectraCosineScore, Metadata, XML, Locale, Version, Library, \
  LabGroup, UserTask, UserTaskStatus
from files.models import UserFile
import json
import sqlite3
from django.contrib.auth.decorators import login_required
from mdb.utils import *

@login_required
def add_sqlite(request):
  if request.method == 'POST':
    form = LoadSqliteForm(request.POST, request.FILES)
    if form.is_valid():
      result = handle_uploaded_file(request, form)
      return redirect('chat:user_tasks')
  else:
    form = LoadSqliteForm()
  return render(request, 'importer/add_sqlite.html', {'form': form})

def handle_uploaded_file(request, tmpForm):
  '''
  Spectra is inserted last as it depends on XML and Metadata tables.
  Requires json and sqlite3 libraries.
  Metadata strain_id and XML xml_hash should both be unique but they
  are not in R01 data?
  
  :param tmpForm: Copy of the LoadSqliteForm
  '''
  if request.FILES and request.FILES['file']:
    f = request.FILES['file']
    with open('/tmp/test.db', 'wb+') as destination:
      for chunk in f.chunks():
        destination.write(chunk)
    t = UserTask.objects.create(
      owner = request.user,
      task_description = 'idbac_sql'
    )
    t.statuses.add(UserTaskStatus.objects.create(status = 'start'))
    t.statuses.add(UserTaskStatus.objects.create(
      status = 'info',
      extra = 'Loading SQLite file ' + str(f),
      user_task = t
    ))
    thread = _insert(request, tmpForm, '/tmp/test.db', t)
  elif tmpForm.cleaned_data['upload_type'] == 'all': # hosted on server
    hc = [
      '2019_04_15_10745_db-2_0_0.sqlite',
      '2019_06_06_22910_db-2_0_0.sqlite',
      '2019_06_12_10745_db-2_0_0.sqlite',
      '2019_07_02_22910_db-2_0_0.sqlite',
      '2019_07_10_10745_db-2_0_0.sqlite',
      '2019_07_17_1003534_db-2_0_0.sqlite',
      '2019_09_04_10745_db-2_0_0.sqlite',
      '2019_09_11_1003534_db-2_0_0.sqlite',
      '2019_09_18_22910_db-2_0_0.sqlite',
      '2019_09_25_10745_db-2_0_0.sqlite',
      '2019_10_10_1003534_db-2_0_0.sqlite',
      '2019_11_13_1003534_db-2_0_0.sqlite',
      '2019_11_20_1003534_db-2_0_0.sqlite',
    ]
    for f in hc:
      t = UserTask.objects.create(
        owner = request.user,
        task_description = 'idbac_sql'
      )
      t.statuses.add(UserTaskStatus.objects.create(
        status = 'start',
        user_task = t
      ))
      t.statuses.add(UserTaskStatus.objects.create(
        status = 'info',
        extra = 'Loading SQLite file ' + f,
        user_task = t
      ))
      _insert(request, tmpForm, '/home/app/web/r01data/' + f, t)
    
@start_new_thread
def _insert(request, tmpForm, uploadFile, user_task):
  '''
  
  In the case of erroneous data, save the row data to user's
  error log. E.g., if mass, intensity, or snr contain "na" or "nan".
  Wrap entire insert in try-catch, noting errors for 
  later inspection.
  
  '''  
  try:
    idbac_sqlite_insert(request, tmpForm, uploadFile, user_task)
  except Exception as e:
    user_task.statuses.add(
      UserTaskStatus.objects.create(
        status = 'error',
        extra = 'Unexpected except caught\n{}: {}'.format(type(e).__name__, e),
        user_task = user_task
    ))
  finally:
    user_task.statuses.add(
      UserTaskStatus.objects.create(
        status = 'complete', user_task = user_task
    ))

def idbac_sqlite_insert(request, tmpForm, uploadFile, user_task = False):
  '''
  Unique: Library + Metadata.strain_id, Library + XML.xml_hash
  Version 1: Overwrites unique entries. TODO: User feedback.
  
  :return: Optionally returns an info object detailing results
  '''
  idbac_version = '1.0.0'
  connection = sqlite3.connect(uploadFile)
  cursor = connection.cursor()
  info = {
    'spectra': {
      'protein': 0,
      'sm': 0
    }
  }
  
  # Version
  rows = cursor.execute("SELECT * FROM version").fetchall()
  for row in rows:
    idbac_version = row[2] if len(row) == 3 else '1.0.0'
    data = {
      'idbac_version': row[0],
      'r_version': row[1],
      'db_version': idbac_version,
    }
    form = VersionForm(data)
    if form.is_valid():
      entry = form.save(commit = False)
      entry.save()
    else:
        raise ValueError('xxxxx')
        
  # Metadata
  if user_task:
    user_task.statuses.add(
      UserTaskStatus.objects.create(
        status = 'info', extra = 'Inserting metadata',
        user_task = user_task
    ))
  rows = cursor.execute("SELECT * FROM metaData").fetchall()
  for row in rows:
    data = {
      'strain_id': row[0],
      'genbank_accession': row[1],
      'ncbi_taxid': row[2],
      'cKingdom': row[3],
      'cPhylum': row[4],
      'cClass': row[5],
      'cOrder': row[6],
      'cGenus': row[7],
      'cSpecies': row[8],
      'maldi_matrix': row[9],
      'dsm_cultivation_media': row[10],
      'cultivation_temp_celsius': row[11],
      'cultivation_time_days': row[12],
      'cultivation_other': row[13],
      'user_firstname_lastname': row[14],
      'user_orcid': row[15],
      'pi_firstname_lastname': row[16],
      'pi_orcid': row[17],
      'dna_16s': row[18],
      'created_by': request.user.id,
      'library': tmpForm.cleaned_data['library'].id,
      # ~ 'lab': tmpForm.cleaned_data['lab'].id,
    }
    m1 = False
    try:
      m1 = Metadata.objects.get(strain_id__exact = row[0],
        library = tmpForm.cleaned_data['library']
      )
      form = MetadataForm(data, instance = m1)
    except Metadata.DoesNotExist:
      form = MetadataForm(data)
    except Metadata.MultipleObjectsReturned: # should not occur
      raise ValueError('unique constraint failed on metadata!')
    except:
      pass
    
    if form.is_valid():
      entry = form.save(commit = False)
      entry.save()
    else:
      print(form.errors)
      raise ValueError('xxxxx')
  
  # XML
  if user_task:
    user_task.statuses.add(
      UserTaskStatus.objects.create(
        status = 'info', extra = 'Inserting XML', user_task = user_task
    ))
  rows = cursor.execute("SELECT * FROM XML").fetchall()
  for row in rows:
    data = {
      'xml_hash': row[0],
      'xml': row[1],
      'manufacturer': row[2],
      'model': row[3],
      'ionization': row[4],
      'analyzer': row[5],
      'detector': row[6],
      'instrument_metafile': row[7],
      'created_by': request.user.id,
      'library': tmpForm.cleaned_data['library'].id,
      # ~ 'lab': tmpForm.cleaned_data['lab'].id,
    }
    m1 = False
    try:
      m1 = XML.objects.get(xml_hash__exact = row[0],
        library = tmpForm.cleaned_data['library']
      )
      form = XmlForm(data, instance = m1)
    except XML.DoesNotExist:
      form = XmlForm(data)
    except XML.MultipleObjectsReturned: # should not occur
      raise ValueError('unique constraint failed on xml!')
    except:
      pass
      
    # ~ form = XmlForm(data)
    if form.is_valid():
      entry = form.save(commit = False)
      entry.save()
    else:
      form.non_field_errors()
      field_errors = [(field.label, field.errors) for field in form] 
      raise ValueError('xxxxx')
  
  # Locale
  # Works. Skip for now.
  # ~ rows = cursor.execute("SELECT * FROM locale").fetchall()
  # ~ for row in rows:
    # ~ data = {
      # ~ 'locale': row[0],
    # ~ }
    # ~ form = LocaleForm(data)
    # ~ if form.is_valid():
      # ~ entry = form.save(commit = False)
      # ~ entry.save()
    # ~ else:
        # ~ raise ValueError('xxxxx')
    
  # Spectra
  # row[5] spectrumIntensity ?
  if user_task:
    user_task.statuses.add(
      UserTaskStatus.objects.create(
        status = 'info', extra = 'Inserting spectra',
        user_task = user_task
    ))
  t = 'IndividualSpectra' if idbac_version == '1.0.0' else 'spectra'
  rows = cursor.execute('SELECT * FROM ' + t).fetchall()
  strains = set() # Python set
  for row in rows:
    sxml = XML.objects.filter(xml_hash = row[2])
    if sxml:
      sxml = sxml[0]
    smd = Metadata.objects.filter(strain_id = row[3])
    if smd:
      smd = smd[0]
    pm = json.loads(row[4])
    
    data = {
      'created_by': request.user.id,
      'library': tmpForm.cleaned_data['library'].id,
      # ~ 'lab': tmpForm.cleaned_data['lab'].id,
      'privacy_level': tmpForm.cleaned_data['privacy_level'][0],
      
      'spectrum_mass_hash': row[0],
      'spectrum_intensity_hash': row[1],
      
      'xml_hash': sxml.id,
      'strain_id': smd.id,
      'peak_mass': ','.join(map(str, pm['mass'])),
      'peak_intensity': ','.join(map(str, pm['intensity'])),
      'peak_snr': ','.join(map(str, pm['snr'])),
      
      'max_mass': row[6],
      'min_mass': row[7],
      'spot': row[36]
    }
    
    # Sanity check ("na" or "nan"): Skip this spectra.
    # There are a few NA spectras in R01 data
    if 'na' in row[4].lower():
      if user_task:
        user_task.statuses.add(
          UserTaskStatus.objects.create(
            status = 'error',
            extra = 'Peak mass, intensity, or SNR contains an "NA" value:\n\n'
              'Row data:\n\n' + json.dumps(data),
            user_task = user_task
        ))
      continue
    
    m1 = False
    try:
      m1 = Spectra.objects.get(spectrum_mass_hash = row[0],
        spectrum_intensity_hash = row[1],
        library = tmpForm.cleaned_data['library']
      )
      form = SpectraForm(data, instance = m1)
      print('spectra exists! overwriting')
    except Spectra.DoesNotExist:
      form = SpectraForm(data)
      print('new spectra!')
    except Spectra.MultipleObjectsReturned: # should not occur
      raise ValueError('unique constraint failed on spectra!')
    except:
      pass
      
    # ~ form = SpectraForm(data)
    if form.is_valid():
      entry = form.save(commit = False)
      entry.save()
      strains.add(smd.id)
      info['spectra']['protein' if row[6] > 6000 else 'sm'] += 1
    else:
      form.non_field_errors()
      field_errors = [(field.label, field.errors) for field in form]
      raise ValueError('xxxxx')
  
  from django.db import connection
  connection.close()
  
  return info

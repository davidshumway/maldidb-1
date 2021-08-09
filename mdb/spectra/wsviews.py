'''
Spectra websocket views
'''
from chat.models import Library, Metadata
from chat.forms import MetadataForm
from .models import *
from spectra.models import *
from django.db.models import Count
import websocket
import json
import requests
from mdb.utils import *
from files.models import UserFile

def _cosine_score_libraries(libraries):
  '''
  '''
  # Checks if manytomany scoring already exists
  # e.g. https://stackoverflow.com/questions/16324362/
  # django-queryset-get-exact-manytomany-lookup
  q = LibrariesCosineScore.objects.annotate(count = Count('libraries'))\
    .filter(count = len(libraries))
  for lid in libraries:
    q = q.filter(libraries = lid)
  if len(q) > 0:
    return lib_score_parseresult(q[0].result)
  
  # Checks libraries exist
  try:
    lib_cos_score = LibrariesCosineScore.objects.create(
      result = '' 
    )
    for lid in libraries:
      lib_cos_score.libraries.add(Library.objects.get(id = lid))
    lib_cos_score.save()
  except Exception as e:
    # e.g. if a Library id doesn't exist
    print('e:', e)
    return
  
  # Creates a new score
  data = {
    'ids': libraries
  }
  r = requests.post(
    'http://plumber:8000/cosineLibCompare',
    params = data
  )
  # Writes result to db
  if r.status_code == 200:
    lib_cos_score.result = r.text
    lib_cos_score.save()
    return lib_score_parseresult(r.text)
    
@start_new_thread
def cosine_score_libraries(self, val, client):
  '''
  '''
  try:
    r = _cosine_score_libraries(val['libraries'])
    ws = websocket.WebSocket()
    ws.connect('ws://localhost:8000/ws/pollData')
    ws.send(json.dumps({
      'type': 'library comparison result',
      'data': {
        'client': client,
        'result': r
      }
    }))
    ws.close()
  except Exception as e:
    print(e)
    pass
  
def lib_score_parseresult(result):
  r = json.loads(result)
  x = []
  c1 = 0
  for i in r['ids']:
    edges = []
    c2 = 0
    for j in r['similarity'][c1]:
      edges.append({
        'id': r['ids'][c2][0],
        's': r['similarity'][c1][c2]
      })
      c2 += 1
    x.append({
      'id': r['ids'][c1][0],
      'lid': r['lib_ids'][c1][0],
      'edges': edges
    })
    c1 += 1
  return x

@start_new_thread
def apply_csv_metadata(self, csv_ids, library_id):
  '''
  
  Cols: New strain name,Old strain name,Genbank accession,Ncbi taxid,Kingdom,
    Phylum,Class,Order,Family,Genus,Species,Subspecies,Maldi matrix,
    Dsm cultivation media,Cultivation temp celsius,Cultivation time days,
    Cultivation other,User firstname lastname,User orcid,
    Pi firstname lastname,Pi orcid,Dna 16s
  '''
  files = UserFile.objects.filter(id__in = csv_ids) #library_id = library_id, extension = 'csv'
  print(f'files{files}')
  # ~ files = UserFile.objects.filter(id__in = Library.objects.filter(library_id = library_id)[0].user_files,
    # ~ extension = 'csv')
  
  for uf in files:
    #lines = uf.file.open('r').readlines()
    #for line in lines:
    t = UserTask.objects.create(
      owner = self.scope['user'],
      task_description = 'metadata'
    )
    t.statuses.add(UserTaskStatus.objects.create(status = 'start'))
    import csv
    with open(uf.file.path, newline = '') as csvfile:
      reader = csv.DictReader(csvfile)
      row0 = True
      for row in reader:
        if row0 == True:
          row0 = False
          continue
        # ~ print(f'row{row}')
        try:
          data = {
            'strain_id': row['New strain name'],
            'genbank_accession': row['Genbank accession'],
            'ncbi_taxid': row['Ncbi taxid'],
            'cKingdom': row['Kingdom'],
            'cPhylum': row['Phylum'],
            'cClass': row['Class'],
            'cOrder': row['Order'],
            'cFamily': row['Family'],
            'cGenus': row['Genus'],
            'cSpecies': row['Species'],
            'maldi_matrix': row['Maldi matrix'],
            'dsm_cultivation_media': row['Dsm cultivation media'],
            'cultivation_temp_celsius': row['Cultivation temp celsius'],
            'cultivation_time_days': row['Cultivation time days'],
            'cultivation_other': row['Cultivation other'],
            'user_firstname_lastname': row['User firstname lastname'],
            'user_orcid': row['User orcid'],
            'pi_firstname_lastname': row['Pi firstname lastname'],
            'pi_orcid': row['Pi orcid'],
            'dna_16s': row['Dna 16s'],
            'created_by': self.scope['user'].id,# request.user.id,
            'library': library_id,
          }
        except Exception as e:
          t.statuses.add(
            UserTaskStatus.objects.create(
              status = 'error',
              extra = 'Unexpected exception\n{}: {}'.format(type(e).__name__, e),
              user_task = t
          ))
          continue
        # ~ m1 = False
        # ~ s1 = False
        # ~ s2 = False
        try:
          m1, bool_cr1 = Metadata.objects.get_or_create(
            strain_id = row['Old strain name'],
            library_id = library_id)
        except Exception as e:
          t.statuses.add(
            UserTaskStatus.objects.create(
              status = 'error',
              extra = 'Unexpected exception\n{}: {}'.format(type(e).__name__, e),
              user_task = t
          ))
          continue
        try:
          m2, bool_cr2 = Metadata.objects.get_or_create(
            strain_id = row['New strain name'],
            library_id = library_id)
        except Exception as e:
          t.statuses.add(
            UserTaskStatus.objects.create(
              status = 'error',
              extra = 'Unexpected exception\n{}: {}'.format(type(e).__name__, e),
              user_task = t
          ))
          continue
        # Updates spectra
        s1 = Spectra.objects.filter(
          strain_id__strain_id = row['Old strain name'],
          library_id = library_id)
        s2 = CollapsedSpectra.objects.filter(
          strain_id__strain_id = row['Old strain name'],
          library_id = library_id)
        s1.update(strain_id = m2)
        s2.update(strain_id = m2)
  # Relays status to ui
  ws = websocket.WebSocket()
  ws.connect('ws://localhost:8000/ws/pollData')
  ws.send(json.dumps({
    'type': 'completed apply csv metadata',
    'data': { 'client': self.client_id }
  }))
  ws.close()
        
@start_new_thread
def collapse_lib(self, library, client, search_library):
  '''
  Collapses a library and optionally starts cosine scoring during file upload
  
  In the case that metadata was added to the library, the metadata is
  applied at this point.
  
  :param int library: User's library
  :param search_library: Optional library ID (int) from upload+search, or
    False (bool) if upload
  :return: No return value but communicates status to client through a
    ws connection
  '''
  data = { 'id': library, 'owner': self.scope['user'].id }
  r = requests.get(
    'http://plumber:8000/collapseLibrary',
    params = data
  )
  
  # relays it's done and sends back ids
  n1 = CollapsedSpectra.objects.filter( # unknown spectra
    library_id__exact = library,
    spectra_content__exact = 'PR') \
    .order_by('id').select_related('strain_id__strain_id') \
    .values('id', 'strain_id', 'strain_id__strain_id', 'library_id')
  
  ws = websocket.WebSocket()
  ws.connect('ws://localhost:8000/ws/pollData')
  ws.send(json.dumps({
    'type': 'completed collapsing',
    'data': {
      'client': client,
      'results': [{
        'id': s['id'],
        'strain_id': s['strain_id'],
        'strain_id__strain_id': s['strain_id__strain_id']
      } for s in list(n1)]
    }
  }))
  ws.close()
  
  # Performs cosine scoring
  if search_library is not False:
    cosine_scores(self, library, client, search_library)

@start_new_thread
def cosine_scores_existing(self, library, client, search_library):
  # Relays it's "done" and sends back ids
  n1 = CollapsedSpectra.objects.filter( # unknown spectra
    library_id__exact = library,
    spectra_content__exact = 'PR') \
    .order_by('id').select_related('strain_id__strain_id') \
    .values('id', 'strain_id', 'strain_id__strain_id', 'library_id')
  ws = websocket.WebSocket()
  ws.connect('ws://localhost:8000/ws/pollData')
  ws.send(json.dumps({
    'type': 'completed collapsing',
    'data': {
      'client': client,
      'results': [{
        'id': s['id'],
        'strain_id': s['strain_id'],
        'strain_id__strain_id': s['strain_id__strain_id']
      } for s in list(n1)]
    }
  }))
  ws.close()
  cosine_scores(self, library, client, search_library)

@start_new_thread
def single_score(self, client, msg):
  '''
  Returns a full score (dendrogram + scores)
  
  Assumes that the score exists.
  
  :param msg['spectra1']: Collapsed spectra ID of unknown sample
  :param msg['searchLibrary']: Library ID of known entries
  '''
  ws = websocket.WebSocket()
  ws.connect('ws://localhost:8000/ws/pollData')
  
  ccs = None
  try:
    obj = CollapsedCosineScore.objects.get(
      spectra = msg['spectra1'],
      library = Library.objects.get(id = msg['searchLibrary']))
    ccs = json.loads(obj.result)
    spectra1 = CollapsedSpectra.objects.get(id = msg['spectra1'])
  except CollapsedSpectra.DoesNotExist:
    print('CollapsedSpectra.DoesNotExist')
    ws.close()
    return
  except CollapsedCosineScore.DoesNotExist:
    print('CollapsedSpectra.DoesNotExist')
    ws.close()
    return
  except Library.DoesNotExist:
    print('Library.DoesNotExist')
    ws.close()
    return
  except Exception as e:
    print(e)
    ws.close()
    return
  
  n2 = CollapsedSpectra.objects.filter(
    library = msg['searchLibrary'],
    spectra_content__exact = 'PR'
  ).order_by('id').values('id', 'strain_id__strain_id',
    'strain_id__cSpecies', 'strain_id__cGenus', 'strain_id__cFamily',
    'strain_id__cOrder', 'strain_id__cClass', 'strain_id__cPhylum',
    'strain_id__cKingdom', 'peak_mass', 'peak_intensity')
  
  # Creates dict of n2
  search_lib_dict = {str(value['id']): value for value in list(n2)}
  
  # Creates dictionary of binned peaks
  tmp = ccs['binnedPeaks']
  binned_peaks = {}
  for v in tmp:
    binned_peaks[str(v['csId'][0])] = {
      'mass': v['mass'],
      'intensity': v['intensity'],
      'snr': v['snr'],
    }
  
  # Creates dictionary sorted by its values (similarity score)
  from collections import OrderedDict
  k = [str(s['id']) for s in list(n2)] # one less
  v = ccs['similarity'][1:] # one more remove first??
  score_dict = OrderedDict(
    sorted(dict(zip(k, v)).items(),
      key = lambda x: (x[1], x[0]), reverse = True)
  )
  
  u = ['Unknown sample']
  result = {
    'scores': [],
    'dendro': ccs['dendro'],
    'original': {
      'peak_mass': spectra1.peak_mass,
      'peak_intensity': spectra1.peak_intensity,
      'binned_mass': binned_peaks[str(msg['spectra1'])]['mass'],
      'binned_intensity': binned_peaks[str(msg['spectra1'])]['intensity'],
      'binned_snr': binned_peaks[str(msg['spectra1'])]['snr'],
    }
  }
  
  rowcount = 1
  for (idx, id) in enumerate(score_dict): # e.g. 0 '12346' 0.2
    s = search_lib_dict[id]
    result['scores'].append({
      'score': score_dict[id],
      'id': id,
      'strain': s['strain_id__strain_id'],
      
      # ~ 'kingdom': cs.strain_id.cKingdom,
      # ~ 'phylum': cs.strain_id.cPhylum,
      # ~ 'class': cs.strain_id.cClass,
      # ~ 'order': cs.strain_id.cOrder,
      
      # ~ 'peak_mass': cs.peak_mass,
      # ~ 'peak_intensity': cs.peak_intensity,
      
      'family': s['strain_id__cFamily'],
      'genus': s['strain_id__cGenus'],
      'species': s['strain_id__cSpecies'],
      'rowcount': rowcount,
      
      'peak_mass': s['peak_mass'],
      'peak_intensity': s['peak_intensity'],
      'binned_mass': binned_peaks[id]['mass'],
      'binned_intensity': binned_peaks[id]['intensity'],
      'binned_snr': binned_peaks[id]['snr'],
    })
  ws.send(json.dumps({
    'type': 'single score result',
    'data': {
      'client': client,
      'result': result,
      'spectra1': spectra1.id
    }
  }))
  ws.close()
  
def cosine_scores(self, library, client, search_library):
  '''Performs cosine for unknown library against a known one.
  '''
  ws = websocket.WebSocket()
  ws.connect('ws://localhost:8000/ws/pollData')
  
  try:
    search_library_obj = Library.objects.get(id = search_library)
  except Library.DoesNotExist:
    print('Search library does not exist?')
    ws.close()
    return
    
  n1 = CollapsedSpectra.objects.filter( # unknown spectra
    library_id__exact = library,
    spectra_content__exact = 'PR'
  )
  n2 = CollapsedSpectra.objects.filter(
    # ~ library_id__exact = search_library,
    library = search_library,
    spectra_content__exact = 'PR'
  ).order_by('id').values('id', 'strain_id__strain_id',
    'strain_id__cSpecies', 'strain_id__cGenus', 'strain_id__cFamily',
    'strain_id__cOrder', 'strain_id__cClass', 'strain_id__cPhylum',
    'strain_id__cKingdom')
  
  # makes a dict of n2 to avoid another hit to db later
  search_lib_dict = {str(value['id']): value for value in list(n2)}
  
  # ~ n2 = CollapsedSpectra.objects.filter(library_id = 12937, spectra_content__exact = 'PR').order_by('id').values('id', 'strain_id__strain_id',    'strain_id__cSpecies', 'strain_id__cGenus', 'strain_id__cFamily', 'strain_id__cOrder', 'strain_id__cClass', 'strain_id__cPhylum', 'strain_id__cKingdom')
  
  # TEST ONLY clears ccs cache
  # ~ print('clear ccs cache')
  # ~ CollapsedCosineScore.objects.all().delete()
  # ~ print('done clear')
  
  # TODO: Provide user feedback of issue
  if len(n2) == 0:
    print('No collapsed spectra in search library!')
    ws.close()
    return
  
  # Inserts into cache after sending data back to client,
  # and in addition uses bulk_create rather than create.
  # Caching the score to db on each loop iteration results in
  # 100x slowdown (e.g. 5 seconds per iteration versus 0.05 seconds).
  collapsed_score_objects = []
  
  # Performs cosine score for every unknown spectra in first library
  for spectra1 in n1:
    
    # Checks if there is already an existing score
    ccs = None
    try:
      obj = CollapsedCosineScore.objects.get(
        spectra = spectra1,
        library = search_library_obj)
      # exists
      ccs = json.loads(obj.result)
    except CollapsedCosineScore.DoesNotExist:
      data = {
        'ids': [spectra1.id] + [s['id'] for s in list(n2)]
      }
      r = requests.post(
        'http://plumber:8000/cosine',
        params = data
      )
      if r.status_code != 200: # ??
        ws.close()
        print(r.status_code)
        return
      
      # Awaits db write until all scores are sent back to client
      # Downside: If two clients are asking for the same search ("lib1 vs. lib2"),
      #  then no chance to work together.
      collapsed_score_objects.append(CollapsedCosineScore(
        spectra = spectra1,
        library = search_library_obj,
        result = r.text
      ))
      ccs = r.json()
    
    # Returns shorter version, while "explore more" returns full data
    
    # Creates dictionary sorted by its values (similarity score)
    from collections import OrderedDict
    k = [str(s['id']) for s in list(n2)] # one less
    v = ccs['similarity'][1:] # one more remove first??
    score_dict = OrderedDict(
      sorted(dict(zip(k, v)).items(),
        key = lambda x: (x[1], x[0]), reverse = True)
    )
    
    u = ['Unknown sample']
    result = {
      'scores': [],
      'ids': {
        'strain': u + [str(s['strain_id__strain_id']) for s in list(n2)],
        'kingdom': u + [str(s['strain_id__cKingdom']) if s['strain_id__cKingdom'] != '' else 'N/A' for s in list(n2)],
        'phylum': u + [str(s['strain_id__cPhylum']) if s['strain_id__cPhylum'] != '' else 'N/A' for s in list(n2)],
        'class': u + [str(s['strain_id__cClass']) if s['strain_id__cClass'] != '' else 'N/A' for s in list(n2)],
        'order': u + [str(s['strain_id__cOrder']) if s['strain_id__cOrder'] != '' else 'N/A' for s in list(n2)],
        'family': u + [str(s['strain_id__cFamily']) if s['strain_id__cFamily'] != '' else 'N/A' for s in list(n2)],
        'genus': u + [str(s['strain_id__cGenus']) if s['strain_id__cGenus'] != '' else 'N/A' for s in list(n2)],
        'species': u + [str(s['strain_id__cSpecies']) if s['strain_id__cSpecies'] != '' else 'N/A' for s in list(n2)]
      },
    }
    
    rowcount = 1
    for (idx, id) in enumerate(score_dict): # e.g. 0 '12346' 0.2
      s = search_lib_dict[id]
      result['scores'].append({
        'score': score_dict[id],
        'id': id,
        'strain': s['strain_id__strain_id'],

        # ~ 'kingdom': cs.strain_id.cKingdom,
        # ~ 'phylum': cs.strain_id.cPhylum,
        # ~ 'class': cs.strain_id.cClass,
        # ~ 'order': cs.strain_id.cOrder,

        'family': s['strain_id__cFamily'],
        'genus': s['strain_id__cGenus'],
        'species': s['strain_id__cSpecies'],
        'rowcount': rowcount,
      })
      rowcount += 1
      if rowcount >= 5:
        break
    ws.send(json.dumps({
      'type': 'completed cosine',
      'data': {
        'client': client,
        'result': result,
        'spectra1': spectra1.id
      }
    }))
    continue
    
  # closes socket
  ws.close()
  
  # caches the scores for next time (after client has received data)
  CollapsedCosineScore.objects.bulk_create(collapsed_score_objects)
  
  


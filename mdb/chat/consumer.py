from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer
import json
import requests
from chat.models import Library
from mdb.utils import *
import uuid
from spectra.models import *
import websocket

from ncbitaxonomy.models import TxNode
from ncbitaxonomy.views import *
  
# example: https://www.etemkeskin.com/index.php/2021/02/08/
# real-time-application-development-using-websocket-in-django/

clients = {}

class DashConsumer(AsyncJsonWebsocketConsumer):
  
  async def connect(self):
    # ~ print('==================1')
    
    self.client_id = str(uuid.uuid4())
    clients[self.client_id] = self
    
    self.groupname = 'dashboard'
    await self.channel_layer.group_add(
      self.groupname,
      self.channel_name,
    )
    await self.accept()
    
    await self.send_json({'data': {'ip': self.client_id}})

  async def disconnect(self, close_code):
    # ~ print('==================2')
    await self.channel_layer.group_discard(
      self.groupname,
      self.channel_name
    )

  async def receive(self, text_data):
    '''
    '''
    # ~ print('==================3')
    try:
      val = json.loads(text_data)
    except Exception as e:
      print(e)
      return
    
    # client asks to search existing
    try:
      if 'existingLibrary' in val and 'searchLibrary' in val:
        cosine_scores_existing(self, val['existingLibrary'],
          self.client_id, val['searchLibrary'])
    except Exception as e:
      print(e)
      pass
    # client asks for full data of single score
    try:
      if val['type'] == 'single score':
        single_score(self, self.client_id, val)
    except Exception as e:
      print(e)
      pass
    # tells client single score result
    try:
      if val['type'] == 'single score result':
        d = json.dumps({
          'data': {
            'message': 'single score result',
            'data': val['data']
          }
        })
        await clients[val['data']['client']].send(text_data = d)
    except Exception as e:
      print(e)
      pass
      
    ## file upload ##
    
    # tells client preprocessing is complete
    try:
      if val['type'] == 'completed preprocessing':
        d = json.dumps({
          'data': {
            'message': 'completed preprocessing',
            'count': val['data']['count']
          }
        })
        await clients[val['data']['client']].send(text_data = d)
    except Exception as e:
      print(e)
      pass
    
    # client asks to collapse library
    try:
      if val['type'] == 'collapse library':
        collapse_lib(self, val['collapseLibrary'], self.client_id,
          val['searchLibrary'])
    except Exception as e:
      print(e)
      pass
      
    # tells client collapse completed
    try:
      if val['type'] == 'completed collapsing':
        d = json.dumps({
          'data': {
            'message': 'completed collapsing',
            'data': val['data']
          }
        })
        await clients[val['data']['client']].send(text_data = d)
    except Exception as e:    
      print(e)
      pass
      
    # tells client cosine completed
    try:
      if val['type'] == 'completed cosine':
        d = json.dumps({
          'data': {
            'message': 'completed cosine',
            'data': val['data']
          }
        })
        await clients[val['data']['client']].send(text_data = d)
    except Exception as e:    
      print(e)
      pass
    
    ## ncbi alignment ##
    
    # client asks for alignment
    try:
      if val['type'] == 'align':
        align(self, val, self.client_id)
    except Exception as e:    
      print(e)
      pass
    # send align status update
    try:
      if val['type'] == 'align status':
        d = json.dumps({
          'data': {
            'message': 'align status',
            'data': val['data']
          }
        })
        await clients[val['data']['client']].send(text_data = d)
    except Exception as e:    
      print(e)
      pass
    # sends back alignment data
    try:
      if val['type'] == 'completed align':
        d = json.dumps({
          'data': {
            'message': 'completed align',
            'data': val['data']
          }
        })
        await clients[val['data']['client']].send(text_data = d)
    except Exception as e:    
      print(e)
      pass
    # client saves alignment
    try:
      if val['type'] == 'save align':
        save_align(self, val, self.client_id)
    except Exception as e:
      print(e)
      pass
    # sends save alignment success
    try:
      if val['type'] == 'completed save align':
        d = json.dumps({
          'data': {
            'message': 'completed save align',
            'data': val['data']
          }
        })
        await clients[val['data']['client']].send(text_data = d)
    except Exception as e:    
      print(e)
      pass
    # client asks for manual alignment
    try:
      if val['type'] == 'manual_align':
        manual_align(self, val, self.client_id)
    except Exception as e:    
      print(e)
      pass
    # sends manual alignment success
    try:
      if val['type'] == 'completed manual align':
        d = json.dumps({
          'data': {
            'message': 'completed manual align',
            'data': val['data']
          }
        })
        await clients[val['data']['client']].send(text_data = d)
    except Exception as e:    
      print(e)
      pass
    # client asks to save manual alignment
    try:
      if val['type'] == 'save manual align':
        save_manual_align(self, val, self.client_id)
    except Exception as e:    
      print(e)
      pass
    # sends save manual alignment success
    try:
      if val['type'] == 'completed save manual align':
        d = json.dumps({
          'data': {
            'message': 'completed save manual align',
            'data': val['data']
          }
        })
        await clients[val['data']['client']].send(text_data = d)
    except Exception as e:    
      print(e)
      pass
      
  async def deprocessing(self, event):
    print('==================4')
    # ~ await self.send(text_data = json.dumps(event['value']))
  
@start_new_thread
def collapse_lib(self, library, client, search_library):
  '''
  :param str title: Unknown library's title
  :param int search_library: optional lib. ID from upload+search, or
    False if via simple file upload
  '''
  # TODO: Library.objects.filter should account for lab
  # ~ l = Library.objects.filter(title__exact = title,
    # ~ created_by = self.scope['user']).first()
  # ~ if l:
  data = {
    'id': library,
    'owner': self.scope['user'].id
  }
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
  
  # Does cosine scores
  if search_library is not False:
    cosine_scores(self, library, client, search_library)

@start_new_thread
def cosine_scores_existing(self, library, client, search_library):
  #l = Library.objects.filter(title__exact = title,
  #  created_by = self.scope['user']).first()
  
  # relays it's "done" and sends back ids
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
    # ~ rowcount += 1
    # ~ if rowcount >= 10:
      # ~ break
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
  
  print(f'lib {library} sl {search_library}')
  try:
    search_library_obj = Library.objects.get(id = search_library)
  except Library.DoesNotExist:
    print('Search library does not exist?')
    ws.close()
    return
  
  # ~ print(f'search_library_obj {search_library_obj}')
    
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
  
  # ~ search_library_obj
  
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
    
    # Returns shorter version, while explore more returns full data
    
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
      # ~ 'dendro': ccs['dendro'],
      # ~ 'original': {
        # ~ 'peak_mass': spectra1.peak_mass,
        # ~ 'peak_intensity': spectra1.peak_intensity,
        # ~ 'binned_mass': binned_peaks[str(spectra1.id)]['mass'],
        # ~ 'binned_intensity': binned_peaks[str(spectra1.id)]['intensity'],
        # ~ 'binned_snr': binned_peaks[str(spectra1.id)]['snr'],
      # ~ }
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
        
        # ~ 'peak_mass': cs.peak_mass,
        # ~ 'peak_intensity': cs.peak_intensity,
        # ~ 'binned_mass': binned_peaks[id]['mass'],
        # ~ 'binned_intensity': binned_peaks[id]['intensity'],
        # ~ 'binned_snr': binned_peaks[id]['snr'],
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
      'dendro': ccs['dendro'],
      'original': {
        'peak_mass': spectra1.peak_mass,
        'peak_intensity': spectra1.peak_intensity,
        'binned_mass': binned_peaks[str(spectra1.id)]['mass'],
        'binned_intensity': binned_peaks[str(spectra1.id)]['intensity'],
        'binned_snr': binned_peaks[str(spectra1.id)]['snr'],
      }
    }
    
    # ~ from django.db.models import Case, When
    # ~ preserved = Case(*[When(pk = pk, then = pos) for pos, pk in enumerate(o)])
    # ~ q = CollapsedSpectra.objects.filter(id__in = o.keys()).order_by(preserved)[0:4]
    rowcount = 1
    for (idx, id) in enumerate(score_dict): # e.g. 0 '12346' 0.2
      s = search_lib_dict[id]
      result['scores'].append({
        'score': score_dict[id],
        'id': id,
        # ~ 'score': o[str(cs.id)],
        # ~ 'id': cs.id,
        'strain': s['strain_id__strain_id'],
        # ~ 'strain': cs.strain_id.strain_id,
        
        # Add in individual view, if required
        # ~ 'kingdom': cs.strain_id.cKingdom,
        # ~ 'phylum': cs.strain_id.cPhylum,
        # ~ 'class': cs.strain_id.cClass,
        # ~ 'order': cs.strain_id.cOrder,
        
        # ~ 'family': cs.strain_id.cFamily,
        # ~ 'genus': cs.strain_id.cGenus,
        # ~ 'species': cs.strain_id.cSpecies,
        # ~ 'rowcount': rowcount,
        # ~ 'peak_mass': cs.peak_mass,
        # ~ 'peak_intensity': cs.peak_intensity,
        'family': s['strain_id__cFamily'],
        'genus': s['strain_id__cGenus'],
        'species': s['strain_id__cSpecies'],
        'rowcount': rowcount,
        
        # Add in individual view for original spectra view
        # ~ 'peak_mass': cs.peak_mass,
        # ~ 'peak_intensity': cs.peak_intensity,
        'binned_mass': binned_peaks[id]['mass'],
        'binned_intensity': binned_peaks[id]['intensity'],
        'binned_snr': binned_peaks[id]['snr'],
      })
      rowcount += 1
      if rowcount >= 10:
        break
    ws.send(json.dumps({
      'type': 'completed cosine',
      'data': {
        'client': client,
        'result': result,
        'spectra1': spectra1.id
      }
    }))
  
  # closes socket
  ws.close()
  
  # caches the scores for next time (after client has received data)
  CollapsedCosineScore.objects.bulk_create(collapsed_score_objects)
  

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer
import json
import requests
from chat.models import Library
from mdb.utils import *
import uuid
from spectra.models import *
import websocket

# example: https://www.etemkeskin.com/index.php/2021/02/08/
# real-time-application-development-using-websocket-in-django/
# ~ class DashConsumer(WebsocketConsumer):
  # ~ def connect(self):
    # ~ print('==================2')
    # ~ self.accept()

  # ~ def disconnect(self, close_code):
    # ~ print('==================1')
    # ~ pass

  # ~ def receive(self, text_data):
    # ~ print('==================0')
    # ~ text_data_json = json.loads(text_data)
    # ~ message = text_data_json['message']
    # ~ self.send(text_data = json.dumps({
        # ~ 'message': message
      # ~ })
    # ~ )
clients = {}

class DashConsumer(AsyncJsonWebsocketConsumer):
  # ~ users = {}
  
  async def connect(self):
    print('==================1')
    
    #print(f'self.scope{self.scope}')
    # ~ ip = self.scope['client'][0] + ':' + str(self.scope['client'][1])
    # ~ print(f'ip{ip}')
    # ~ self.users[ip] = True
    # ~ print(f'client{clients}')
    #self.pusher = await self.get_pusher(ip)
    #print(self.pusher)
    
    self.client_id = str(uuid.uuid4())
    clients[self.client_id] = self
    
    self.groupname = 'dashboard'
    await self.channel_layer.group_add(
      self.groupname,
      self.channel_name,
    )
    await self.accept()
    
    # ~ await self.send(text_data = json.dumps({"testing from py": True}))
    # ~ await self.send_json({'data': {'ip': ip}})
    
    
    await self.send_json({'data': {'ip': self.client_id}})

  async def disconnect(self, close_code):
    print('==================2')
    await self.channel_layer.group_discard(
      self.groupname,
      self.channel_name
    )

  async def receive(self, text_data):
    '''
    '''
    print('==================3')
    # ~ print ('>>>>', text_data)
    
    # tell client preprocessing is complete
    try:
      val = json.loads(text_data)
      # ~ print(f'val{val}')
      if val['type'] == 'completed preprocessing':
        # ~ print(f'sending to client:{clients[val["data"]["client"]]}')
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
      val = json.loads(text_data)
      if val['collapseLibrary'] != '':
        collapse_lib(self, val['collapseLibrary'], self.client_id,
          val['searchLibrary'])
    except Exception as e:
      print(e)
      pass
    
    # tell client collapse completed
    try:
      val = json.loads(text_data)
      # ~ print(f'val{val}')
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
      
    # tell client collapse completed
    try:
      val = json.loads(text_data)
      print(f'val{val}')
      if val['type'] == 'completed cosine':
        d = json.dumps({
          'data': {
            'message': 'completed cosine',
            'data': val['data']
            # ~ {
              # ~ 'client': client,
              # ~ 'result': result,
              # ~ 'spectra1': spectra1.id
            # ~ }
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
def collapse_lib(self, title, client, search_library):
  '''
  :param str title: Unknown library's title
  :param int search_library: Library ID
  '''
  l = Library.objects.filter(title__exact = title,
    created_by = self.scope['user']).first()
  if l:
    data = {
      'id': l.id,
      'owner': self.scope['user'].id
    }
    r = requests.get(
      'http://plumber:8000/collapseLibrary',
      params = data
    )
    # ~ print(f'r{r}')
    # relays it's done and send back ids
    n1 = CollapsedSpectra.objects.filter( # unknown spectra
      library_id__exact = l.id,
      spectra_content__exact = 'PR') \
      .order_by('id').select_related('strain_id__strain_id') \
      .values('id', 'strain_id', 'strain_id__strain_id')
    
    # ~ CollapsedSpectra.objects.filter(library_id__exact = 1,spectra_content__exact = 'PR').order_by('id').select_related('strain_id').values('id', 'strain_id')
    
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
    
    # Do cosine scores
    cosine_scores(self, l.id, client, search_library)
    
def cosine_scores(self, library, client, search_library):
  '''Performs cosine scoring for unknown library against a known one
  '''
  ws = websocket.WebSocket()
  ws.connect('ws://localhost:8000/ws/pollData')
  
  sl = Library.objects.get(id = search_library)
  
  n1 = CollapsedSpectra.objects.filter( # unknown spectra
    library_id__exact = library,
    spectra_content__exact = 'PR'
  )
  n2 = CollapsedSpectra.objects.filter(
    library__exact = search_library,
    spectra_content__exact = 'PR'
  ).order_by('id').values('id')
  
  for spectra1 in n1:
    data = {
      'ids': [spectra1.id] + [s['id'] for s in list(n2)]
    }
    r = requests.post(
      'http://plumber:8000/cosine',
      params = data
    )
    tmp = r.json()['binnedPeaks']
    binned_peaks = {}
    for v in tmp: # Dictionary of binned peaks
      binned_peaks[str(v['csId'][0])] = {
        'mass': v['mass'],
        'intensity': v['intensity'],
        'snr': v['snr'],
      }
    # Dictionary sorted by its values
    from collections import OrderedDict
    k = [str(s['id']) for s in list(n2)] # one less
    v = r.json()['similarity'][1:] # one more remove first???
    o = OrderedDict(
      sorted(dict(zip(k, v)).items(),
        key = lambda x: (x[1], x[0]), reverse = True)
    )

    obj = CollapsedCosineScore.objects.create(
      spectra = spectra1,
      library = sl, # lib unnecessary in ccs model
      scores = ','.join(map(str, list(o.values()))),
      spectra_ids = ','.join(map(str, o.keys())))
    
    if obj:
      result = {
        'scores': [],
        'original': {
          'peak_mass': spectra1.peak_mass,
          'peak_intensity': spectra1.peak_intensity,
          'binned_mass': binned_peaks[str(spectra1.id)]['mass'],
          'binned_intensity': binned_peaks[str(spectra1.id)]['intensity'],
          'binned_snr': binned_peaks[str(spectra1.id)]['snr'],
        }
      }
      
      from django.db.models import Case, When
      preserved = Case(*[When(pk = pk, then = pos) for pos, pk in enumerate(o)])
      q = CollapsedSpectra.objects.filter(id__in = o.keys()).order_by(preserved)
      rowcount = 1
      for cs in q:
        result['scores'].append({
          'score': o[str(cs.id)],
          'id': cs.id,
          'strain': cs.strain_id.strain_id,
          'kingdom': cs.strain_id.cKingdom,
          'phylum': cs.strain_id.cPhylum,
          'class': cs.strain_id.cClass,
          'order': cs.strain_id.cOrder,
          # ~ 'family': cs.strain_id.cFamily,
          'genus': cs.strain_id.cGenus,
          'species': cs.strain_id.cSpecies,
          'rowcount': rowcount,
          'peak_mass': cs.peak_mass,
          'peak_intensity': cs.peak_intensity,
          'binned_mass': binned_peaks[str(cs.id)]['mass'],
          'binned_intensity': binned_peaks[str(cs.id)]['intensity'],
          'binned_snr': binned_peaks[str(cs.id)]['snr'],
        })
        rowcount += 1
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
  
  
  # ~ data = {
    # ~ 'ids': [l.id, search_library]
  # ~ }
  # ~ r = requests.post(
    # ~ 'http://plumber:8000/cosine2',
    # ~ params = data
  # ~ )

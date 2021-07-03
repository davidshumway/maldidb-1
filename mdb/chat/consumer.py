from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer
import json
import requests
from chat.models import Library
from mdb.utils import *
import uuid
from spectra.models import *
import websocket

from chat.models import Metadata
from ncbitaxonomy.models import TxNode
  
# example: https://www.etemkeskin.com/index.php/2021/02/08/
# real-time-application-development-using-websocket-in-django/

clients = {}

class DashConsumer(AsyncJsonWebsocketConsumer):
  
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
    
    # tells client preprocessing is complete
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
    
    # tells client collapse completed
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
      
    # tells client cosine completed
    try:
      val = json.loads(text_data)
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
    
    # client asks for alignment
    try:
      val = json.loads(text_data)
      if val['type'] == 'align':
        align(self, val, self.client_id)
    except Exception as e:    
      print(e)
      pass
    # send alignment data
    try:
      val = json.loads(text_data)
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
      val = json.loads(text_data)
      if val['type'] == 'save align':
        save_align(self, val, self.client_id)
    except Exception as e:
      print(e)
      pass
    # send save alignment success
    try:
      val = json.loads(text_data)
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
    
  async def deprocessing(self, event):
    print('==================4')
    # ~ await self.send(text_data = json.dumps(event['value']))

def get_parents(txid):
  '''
  :return rslt: List of objects where each object is {name, rank}
  '''
  print(f'txid{txid}')
  n = TxNode.objects.filter(txid = txid)
  if len(n) == 0:
    return []
  else:
    return [n.first()] + get_parents(n.first().parentid) # if n.parentid else [])
  # ~ print(f'node{n}')
  # ~ return 
  

@start_new_thread
def save_align(self, msg, client):
  '''
  :param msg['library']: Library containing metadata
  :param msg['alignments']: Exact matches to update
  '''
  update_nodes = []
  for alignment in msg['alignments']:
    n = Metadata.objects.filter(id = alignment['id'],
      library__id = msg['library']).first()
    n.ncbi_taxid = alignment['exact_txid']
    parents = get_parents(alignment['exact_parentid'])
    for parent in parents:
      #print(f'rank{parent.txtype}')
      if parent.txtype == 'species':
        n.cSpecies = parent.name
      elif parent.txtype == 'genus':
        n.cGenus = parent.name
      elif parent.txtype == 'family':
        n.cFamily = parent.name
      elif parent.txtype == 'order':
        n.cOrder = parent.name
      elif parent.txtype == 'class':
        n.cClass = parent.name
      elif parent.txtype == 'phylum':
        n.cPhylum = parent.name
      elif parent.txtype == 'superkingdom':
        n.cKingdom = parent.name
      else:
        print(f'unknown parent txtype: {parent.name} {parent.txtype}')
      # ~ elif parent.txtype == '':
        # ~ n.c = parent.name
    update_nodes.append(n)
    
  Metadata.objects.bulk_update(update_nodes, 
    ['ncbi_taxid', 'cSpecies', 'cGenus', 'cFamily', 'cOrder', 'cClass',
    'cPhylum', 'cKingdom']
  )
  
  ws = websocket.WebSocket()
  ws.connect('ws://localhost:8000/ws/pollData')
  ws.send(json.dumps({
    'type': 'completed save align',
    'data': {
      'client': client
    }
  }))
  ws.close()
  
@start_new_thread
def align(self, msg, client):
  '''
  Uses name__iexact for case insensitive search.
  
  Example NCBI irregularities (NRRL):
    NRRL-ISP 5314
    NRRL-B-24892
    NRRL-B 24875
    NRRL-792
    NRRL- Y-27449
    NRRL-ISP:5570
    NRRL-ISP 5590 [[Streptomyces bambergiensis]]
    Arthrobacter NRRL-B3728
    Zygorhynchus sp. NRRL 3102
  '''
  from chat.models import Metadata
  from ncbitaxonomy.models import TxNode
  m = Metadata.objects.filter(library__id = msg['library'])
  
  # return a list of objects
  rslt1 = []
  rslt2 = []
  
  for md in m:
    j = TxNode.objects.filter(name__iexact = msg['prefix'].strip() + ' ' + md.strain_id)
    tmp = {
      'id': md.id,
      'strain_id': md.strain_id,
      'exact_name': '',
      'exact_txid': '',
      'exact_txtype': '',
      'exact_parentname': '',
      'exact_parentid': '',
      'partial_type': 'N/A',
      'partial': 'N/A',
    }
    if len(j) > 0:
      j = j.first()
      name = str(TxNode.objects.get(txid = j.txid, nodetype = "s").name)
      parent = TxNode.objects.get(txid = j.parentid, nodetype = "s")
      # ~ tmp['parent'] = j.parentid
      tmp['exact_name'] = name
      tmp['exact_sciname'] = j.name
      tmp['exact_parentname'] = parent.name
      tmp['exact_parentid'] = parent.txid
      tmp['exact_txid'] = j.txid
      tmp['exact_txtype'] = j.txtype
      # ~ tmp['exact'] = f'{j.name} ({name})|type: {j.txtype}|parent: {pname}'
      rslt1.append(tmp)
    else:
      j2 = TxNode.objects.filter(name__contains =  ' ' + md.strain_id)[0:3]
      if len(j2) > 0:
        i = 0
        strout = []
        while i < 2:
          try:
            strout.append(f'{j2[i].name} ({str(j2[i].txid)})')
          except:
            pass
          i += 1
        tmp['partial_type'] = 'space + name'
        tmp['partial'] = '|'.join(strout)
      else:
        j3 = TxNode.objects.filter(name__contains = md.strain_id)[0:3]
        if len(j3) > 0:
          i = 0
          strout = []
          while i < 2:
            try:
              strout.append(f'{j3[i].name} ({str(j3[i].txid)})')
            except:
              pass
            i += 1
          tmp['partial_type'] = 'name only'
          tmp['partial'] = '|'.join(strout)
        else:
          tmp['partial_type'] = 'No partial match'
      rslt2.append(tmp)
    
  ws = websocket.WebSocket()
  ws.connect('ws://localhost:8000/ws/pollData')
  ws.send(json.dumps({
    'type': 'completed align',
    'data': {
      'client': client,
      'result1': rslt1,
      'result2': rslt2
    }
  }))
  ws.close()
  
  return #rslt
  
def skipline(line):
  if '\tauthority\t' in line:
    return True
  if '\tin-part\t' in line:
    return True
  if '\tincludes\t' in line:
    return True
  if '\tsynonym\t' in line:
    return True
  if '\tacronym\t' in line:
    return True
  if '\tblast name\t' in line:
    return True
  if '\tgenbank common name\t' in line:
    return True
  if '\tgenbank synonym\t' in line:
    return True
  if '\tgenbank acronym\t' in line:
    return True
  if '\tcommon name\t' in line:
    return True
  if '\tequivalent name\t' in line:
    return True
  return False
  
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
  
  search_library_obj = Library.objects.get(id = search_library)
  
  n1 = CollapsedSpectra.objects.filter( # unknown spectra
    library_id__exact = library,
    spectra_content__exact = 'PR'
  )
  n2 = CollapsedSpectra.objects.filter(
    library__exact = search_library,
    spectra_content__exact = 'PR'
  ).order_by('id').values('id', 'strain_id__strain_id',
    'strain_id__cSpecies', 'strain_id__cGenus', 'strain_id__cFamily',
    'strain_id__cOrder', 'strain_id__cClass', 'strain_id__cPhylum',
    'strain_id__cKingdom')
  
  if len(n2) == 0:
    print('No collapsed spectra in search library!')
    return
  
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
    
    # Creates a dictionary sorted by its values (similarity score)
    from collections import OrderedDict
    k = [str(s['id']) for s in list(n2)] # one less
    v = r.json()['similarity'][1:] # one more remove first???
    o = OrderedDict(
      sorted(dict(zip(k, v)).items(),
        key = lambda x: (x[1], x[0]), reverse = True)
    )
    
    # ~ strain_ids = ['Unknown sample'] +\
      # ~ [str(s['strain_id__strain_id']) for s in list(n2)]
    # ~ strain_id__cSpecies = ['Unknown sample'] +\
      # ~ [str(s['strain_id__cSpecies']) if s['strain_id__cSpecies'] != '' else 'N/A' for s in list(n2)]
    # ~ strain_id__cGenus = ['Unknown sample'] +\
      # ~ [str(s['strain_id__cGenus']) if s['strain_id__cGenus'] != '' else 'N/A' for s in list(n2)]

    obj = CollapsedCosineScore.objects.create(
      spectra = spectra1,
      library = search_library_obj, # lib unnecessary in ccs model
      scores = ','.join(map(str, list(o.values()))),
      spectra_ids = ','.join(map(str, o.keys())))
    
    if obj:
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
        # ~ 'strain_ids': strain_ids,
        # ~ 'strain_id__cSpecies': strain_id__cSpecies,
        # ~ 'strain_id__cGenus': strain_id__cGenus,
        'dendro': r.json()['dendro'],
        # ~ 'dendro2': r.json()['dendro2'],
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
          'family': cs.strain_id.cFamily,
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
  
  

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
    # ~ print('==================3')
    
    # tells client preprocessing is complete
    try:
      val = json.loads(text_data)
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
      if 'collapseLibrary' in val: # key in val
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
    # send align status update
    try:
      val = json.loads(text_data)
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
    # client asks for manual alignment
    try:
      val = json.loads(text_data)
      if val['type'] == 'manual_align':
        manual_align(self, val, self.client_id)
    except Exception as e:    
      print(e)
      pass
    # send manual alignment success
    try:
      val = json.loads(text_data)
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
      val = json.loads(text_data)
      if val['type'] == 'save manual align':
        save_manual_align(self, val, self.client_id)
    except Exception as e:    
      print(e)
      pass
    # send save manual alignment success
    try:
      val = json.loads(text_data)
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
def save_manual_align(self, msg, client):
  '''
  :param msg['library']: Library containing metadata
  :param msg['alignments']: Exact matches to update
  '''
  update_nodes = []
  for alignment in msg['alignments']:
    n = Metadata.objects.filter(id = alignment['id'])[0]
    if alignment['txid2'] != '':#
      n.ncbi_taxid = alignment['txid2'] # species
      n.cSpecies = alignment['species']
      n.cGenus = alignment['genus']
    else:
      n.ncbi_taxid = alignment['txid1'] # only genus provided
      n.cGenus = alignment['genus']
    
    # gets the genus node
    tx = TxNode.objects.filter(txid = alignment['txid1'], nodetype = 's')[0]
    
    n.cFamily = tx.cFamily
    n.cOrder = tx.cOrder
    n.cClass = tx.cClass
    n.cPhylum = tx.cPhylum
    n.cKingdom = tx.cKingdom
    
    # ~ parents = get_parents(alignment['genus_parentid'])
    # ~ for parent in parents:
      # ~ if parent.txtype == 'family':
        # ~ n.cFamily = parent.name
      # ~ elif parent.txtype == 'order':
        # ~ n.cOrder = parent.name
      # ~ elif parent.txtype == 'class':
        # ~ n.cClass = parent.name
      # ~ elif parent.txtype == 'phylum':
        # ~ n.cPhylum = parent.name
      # ~ elif parent.txtype == 'superkingdom':
        # ~ n.cKingdom = parent.name
      # ~ else: # unknown parent txtype: Terrabacteria group clade ?
        # ~ print(f'unknown parent txtype: {parent.name} {parent.txtype}')
    update_nodes.append(n)
    
  Metadata.objects.bulk_update(update_nodes, 
    ['ncbi_taxid', 'cSpecies', 'cGenus', 'cFamily', 'cOrder', 'cClass',
    'cPhylum', 'cKingdom']
  )
  
  # sends result back to client
  ws = websocket.WebSocket()
  ws.connect('ws://localhost:8000/ws/pollData')
  ws.send(json.dumps({
    'type': 'completed save manual align',
    'data': {
      'client': client
    }
  }))
  ws.close()
  
@start_new_thread
def manual_align(self, msg, client):
  sIDs = [ s.strip() for s in msg['data']['strain_ids'].strip().split('\n') ]
  genus = [ s.strip() for s in msg['data']['genus'].strip().split('\n') ]
  species = [ s.strip() for s in msg['data']['species'].strip().split('\n') ]
  md = Metadata.objects.filter(library_id = msg['library'],
    strain_id__in = sIDs, ncbi_taxid = '')
  
  sID_dict = {}
  idx = 0
  for s in sIDs:
    sID_dict[s] = idx
    idx += 1
  
  result1 = []
  result2 = []
  for m in md:
    if m.strain_id not in sID_dict:
      continue
    idx = sID_dict[m.strain_id]
    g = genus[idx]
    s = species[idx]
    tmp = {
      'id': m.id,
      'sid': m.strain_id,
      'genus': g,
      'species': s,
      'txid1': '',
      'txid2': '',
      'genus_parentid': '',
    }
    j1 = TxNode.objects.filter(name__iexact = g, txtype__exact = 'genus')\
      .values('txid', 'parentid')
    if len(j1) == 1:
      tmp['txid1'] = j1[0]['txid']
      tmp['genus_parentid'] = j1[0]['parentid']
    if s == '': # only genus provided
      if len(j1) == 0:
        tmp['result'] = 'no match'
        result2.append(tmp)
      elif len(j1) > 1:
        tmp['result'] = 'multiple results'
        result2.append(tmp)
      else:
        tmp['result'] = 'exact match'
        tmp['result_type'] = 'genus'
        result1.append(tmp)
    else: # genus + species provided
      # ~ print(f'parentid__in = {[gx["txid"] for gx in list(j1)]}')
      j2 = TxNode.objects.filter(name__iexact = s,
        txtype__exact = 'species',
        parentid__in = [gx['txid'] for gx in list(j1)])
      if len(j2) == 0:
        tmp['result'] = 'no species match'
        result2.append(tmp)
      elif len(j2) > 1:
        tmp['result'] = 'multiple results'
        result2.append(tmp)
      else:
        tmp['result'] = 'exact match'
        tmp['result_type'] = 'species'
        tmp['txid2'] = j2[0].txid
        result1.append(tmp)
  
  # sends result back to client
  ws = websocket.WebSocket()
  ws.connect('ws://localhost:8000/ws/pollData')
  ws.send(json.dumps({
    'type': 'completed manual align',
    'data': {
      'client': client,
      'result1': result1,
      'result2': result2
    }
  }))
  ws.close()
  
# ~ def get_parents(txid):
  # ~ '''
  # ~ :return rslt: List of objects where each object is {name, rank}
  # ~ '''
  # ~ print(f'txid{txid}')
  # ~ n = TxNode.objects.filter(txid = txid, nodetype = 's')
  # ~ if len(n) == 0:
    # ~ return []
  # ~ else:
    # ~ return [n.first()] + get_parents(n.first().parentid) # if n.parentid else [])

@start_new_thread
def save_align(self, msg, client):
  '''
  :param msg['library']: Library containing metadata
  :param msg['alignments']: Exact matches to update
  '''
  update_nodes = []
  for alignment in msg['alignments']:
    n = Metadata.objects.filter(id = alignment['id'])[0]
    n.ncbi_taxid = alignment['exact_txid']
    # ~ n.cSpecies = alignment['exact_sciname']
    
    tx = TxNode.objects.filter(txid = alignment['exact_txid'], nodetype = 's')[0]
    
    n.cSpecies = tx.cSpecies
    n.cGenus = tx.cGenus
    n.cFamily = tx.cFamily
    n.cOrder = tx.cOrder
    n.cClass = tx.cClass
    n.cPhylum = tx.cPhylum
    n.cKingdom = tx.cKingdom
    
    update_nodes.append(n)
    
  Metadata.objects.bulk_update(update_nodes, 
    ['ncbi_taxid', 'cSpecies', 'cGenus', 'cFamily', 'cOrder', 'cClass',
    'cPhylum', 'cKingdom']
  )
  
  # sends result back to client
  ws = websocket.WebSocket()
  ws.connect('ws://localhost:8000/ws/pollData')
  ws.send(json.dumps({
    'type': 'completed save align',
    'data': {
      'client': client
    }
  }))
  ws.close()

def align_getpartial(nodes):
  '''
  Format closest matches in a readable format
  '''
  i = 0
  strout = []
  while i < 2:
    try:
      strout.append(f'{nodes[i].name} ({str(nodes[i].txid)})')
    except:
      pass
    i += 1
  return '|'.join(strout)
  
@start_new_thread
def align(self, msg, client):
  '''
  
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
    NRRL B-2258 [[Streptomyces phaeoviridis]]
  '''
  from chat.models import Metadata
  from ncbitaxonomy.models import TxNode
  import re
  m = Metadata.objects.filter(library__id = msg['library'], ncbi_taxid = '')
  rslt1 = []
  rslt2 = []
  
  ws = websocket.WebSocket()
  ws.connect('ws://localhost:8000/ws/pollData')
  
  idx = 1
  for md in m:
    # ~ if idx % 10 == 0:
    ws.send(json.dumps({
      'type': 'align status',
      'data': {
        'client': client,
        'status': f'Searching {idx} of {len(m)}'
      }
    }))
    idx += 1
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
    
    s = (msg['prefix'].strip() + ' ' if msg['prefix'].strip() != '' else '')\
      + md.strain_id
    j = TxNode.objects.filter(search_vector = s)[0:2]
    if len(j) > 0:
      if j[0].name.lower() == s.lower():
        sciname = TxNode.objects.get(txid = j[0].txid, nodetype = "s").name
        parent = TxNode.objects.get(txid = j[0].parentid, nodetype = "s")
        tmp['exact_name'] = j[0].name
        tmp['exact_sciname'] = sciname
        tmp['exact_parentname'] = parent.name
        tmp['exact_parentid'] = parent.txid
        tmp['exact_txid'] = j[0].txid
        tmp['exact_txtype'] = j[0].txtype
        rslt1.append(tmp)
      else:
        tmp['partial_type'] = f'{s}'
        tmp['partial'] = align_getpartial(j)
        rslt2.append(tmp)
    else: # tries one more (plain text) search
      s2 = re.sub('[^a-zA-Z0-9]', ' ', md.strain_id)
      s2 = (msg['prefix'].strip() + ' ' if msg['prefix'].strip() != '' else '')\
        + s2
      if s2 != s:
        j = TxNode.objects.filter(search_vector = s2)[0:2]
        if len(j) > 0:
          tmp['partial_type'] = f'{s2} (plain text match)'
          tmp['partial'] = align_getpartial(j)
      # in any case, appends result as partial match
      rslt2.append(tmp)
    continue
    
    # iexact (not used)
    # ~ j = TxNode.objects.filter(name__iexact = msg['prefix'].strip() + ' ' + md.strain_id)
    # ~ if len(j) > 0:
      # ~ j = j.first()
      # ~ sciname = TxNode.objects.get(txid = j.txid, nodetype = "s").name
      # ~ parent = TxNode.objects.get(txid = j.parentid, nodetype = "s")
      # ~ tmp['exact_name'] = j.name
      # ~ tmp['exact_sciname'] = sciname
      # ~ tmp['exact_parentname'] = parent.name
      # ~ tmp['exact_parentid'] = parent.txid
      # ~ tmp['exact_txid'] = j.txid
      # ~ tmp['exact_txtype'] = j.txtype
      # ~ rslt1.append(tmp)
    
    # ~ else:
      # ~ tmpnm_ = re.sub('[^a-zA-Z0-9]', ' ', md.strain_id)
      # ~ j2 = TxNode.objects.filter(
        # ~ name__search = msg['prefix'].strip() + ' ' + tmpnm_
      # ~ )[0:2]
      # ~ if len(j2) > 0:
        # ~ tmp['partial_type'] = f'search ({tmpnm_})'
        # ~ tmp['partial'] = align_getpartial(j2)
      # ~ rslt2.append(tmp)
  
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
  
  

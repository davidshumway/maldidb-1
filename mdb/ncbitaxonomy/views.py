from django.shortcuts import render

from chat.models import Library
from mdb.utils import *
import uuid
from spectra.models import *
import websocket
from chat.models import Metadata

from .models import TxNode
import json

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

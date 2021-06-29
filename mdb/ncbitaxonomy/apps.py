from django.apps import AppConfig
import os
# ~ try:
  # ~ from .models import *
  # ~ from chat.models import *
# ~ except:
  # ~ print('ncbi: waiting for Apps to be ready...')
  # ~ pass

class NcbitaxonomyConfig(AppConfig):
  name = 'ncbitaxonomy'
  #verbose_name = "..."
  
  def skipline(self, line):
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
      
  def ready(self):
    '''Checks for and installs ncbi.
    
    NCBI files: https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/
    
    NRRL is "type material"
    '''
    return
    try:
      from .models import TxNode
      print('NCBI: checking NCBI...', len(TxNode.objects.all()[0:1]))
      
      # reads nodes
      # 0=node's id, 1=parent's id, 2=node's rank
      txrank = {}
      f0 = open('/home/app/web/r01data/nodes.dmp', 'r')
      for line in f0.readlines():
        n = line.split('|') 
        txrank[n[0].strip()] =  {
          'parent': n[1].strip(),
          'txtype': n[2].strip(),
          'division': n[4].strip()
        }
      
      # reads names
      f = open('/home/app/web/r01data/names.dmp', 'r')
      count = 0
      txnodes = []
      allnodes = {}
      created_nodes = []
      from chat.models import Metadata
      m = Metadata.objects.filter(library__title__exact = 'R01 Data') \
        .values('strain_id')
      print(f'm{m}')
      r01 = ['NRRL ' + s['strain_id'] for s in list(m)]
      print(f'r01{r01}')
      r01_ = {k: {} for k in r01}
      print(f'r01_{r01_}')
      #'NRRL ' + s.strain_id for s in m]
      for line in f.readlines():
        if self.skipline(line):
          continue
        n = line.split('|')
        if txrank[n[0].strip()]['division'] != '0': # division code 0 = Bacteria
          continue
        if n[1].strip() in r01: #1 "NRRL B-65307"
          r01_[n[1].strip()] = {
            'line': line
          }
      print(f'r01_{r01_}')
      
      return
      #TxNode.objects.all().delete()
      if len(TxNode.objects.all()[0:1]) < 1:
        print('NCBI: not imported, attempting to install')
        try:
          txrank = {}
          f0 = open('/home/app/web/r01data/nodes.dmp', 'r')
          # 0=node's id, 1=parent's id, 2=node's rank
          for line in f0.readlines():
            n = line.split('|') 
            txrank[n[0].strip()] =  {
              'parent': n[1].strip(),
              'txtype': n[2].strip(),
              'division': n[4].strip()
            }
          
          f = open('/home/app/web/r01data/names.dmp', 'r')
          count = 0
          txnodes = []
          allnodes = {}
          created_nodes = []
          for line in f.readlines():
            if self.skipline(line):
              continue
            n = line.split('|')
            # ~ print('txrank:', txrank[n[0].strip()])
            if txrank[n[0].strip()]['division'] != '0': # division code = Bacteria
              continue
            # ~ print('txrank:', txrank[n[0].strip()])
            # ~ break
            nodetype = n[3].strip()
            if nodetype not in ['scientific name', 'type material']:
              print('invalid nodetype:', nodetype)
              break
            # checks for key in allnodes (id + name = unique)
            if n[1].strip() + n[0].strip() not in allnodes:
              allnodes[n[1].strip() + n[0].strip()] = True
              tx = txrank[n[0].strip()]
              txnodes.append(TxNode(
                name = n[1].strip(),
                txid = n[0].strip(),
                nodetype = nodetype[0],
                txtype = tx['txtype'],
                parentid = tx['parent']
              ))
            #count += 1
            #if count % 200000 == 0:
          try:
            # Bulk create: "returns created objects as a list, in
            # the same order as provided"
            created_nodes = TxNode.objects.bulk_create(txnodes)
          except:
            pass # e.g. duplicate unique
          print(f'NCBI: total nodes = {len(TxNode.objects.all())}')
          txnodes = []
          # inserts final set of nodes
          #created_nodes = created_nodes + TxNode.objects.bulk_create(txnodes)
          #print(f'NCBI: total nodes (final) = {len(TxNode.objects.all())}')
          
          # updates parent node
          nodes = {}
          for node in created_nodes:
            nodes[node.txid] = node
          for node in created_nodes:
            try:
              if txrank[node.txid]:
                node.parent = nodes[node.parentid]
            except:
              print(f'found a node w/o parent? {node}')
          TxNode.objects.bulk_update(created_nodes, ['parent'])
            
        except FileNotFoundError:
          print('NCBI: NCBI data files not found')
          pass
        
    except Exception as e:
      print('ncbi: waiting for Apps to be ready...', e)
      pass
      
    
      
    

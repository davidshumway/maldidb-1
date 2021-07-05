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
  
  txnodes = []
  allnodes = {}
  sciname = {}
  
  def skipline(self, line):
    if '\tauthority\t' in line:
      return True
    if '\tin-part\t' in line:
      return True
    if '\tincludes\t' in line:
      return True
    # ~ if '\tsynonym\t' in line:
      # ~ return True
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
  
  def set_parents(self, node):
    '''
    Sets taxonomic rankings of a node
    '''
    # sets node's ranking
    if node.txtype == 'species':
      node.cSpecies = node.name
    elif node.txtype == 'genus':
      node.cGenus = node.name
    elif node.txtype == 'family':
      node.cFamily = node.name
    elif node.txtype == 'order':
      node.cOrder = node.name
    elif node.txtype == 'class':
      node.cClass = node.name
    elif node.txtype == 'phylum':
      node.cPhylum = node.name
    elif node.txtype == 'superkingdom':
      node.cKingdom = node.name
    # sets node's parents
    parents = self.get_parents(node)
    for parent in parents:
      if parent.txtype == 'species':
        node.cSpecies = parent.name
      elif parent.txtype == 'genus':
        node.cGenus = parent.name
      elif parent.txtype == 'family':
        node.cFamily = parent.name
      elif parent.txtype == 'order':
        node.cOrder = parent.name
      elif parent.txtype == 'class':
        node.cClass = parent.name
      elif parent.txtype == 'phylum':
        node.cPhylum = parent.name
      elif parent.txtype == 'superkingdom':
        node.cKingdom = parent.name
    # ~ return node
      # ~ else:
        # ~ print(f'unknown parent txtype: {parent.name} {parent.txtype}')
        
  def get_parents(self, node):
    try:
      n = self.sciname[str(node.parentid)]
      # ~ n = self.allnodes[node.name + str(node.parentid)]
    except: # KeyError
      return []
    return [n] + self.get_parents(n) # if n.parentid else [])
    
  def ready(self):
    '''Checks for and installs ncbi.
    
    NCBI files: https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/
    
    NRRL is "type material"
    '''
    try:
      from .models import TxNode
      print('NCBI: checking NCBI...', len(TxNode.objects.all()[0:1]))
      # ~ return
      
      if len(TxNode.objects.all()[0:1]) < 1:
        print('NCBI: not imported, attempting to install')
        try:
          
          # creates ranking dict
          txrank = {}
          f0 = open('/home/app/web/r01data/nodes.dmp', 'r')
          # 0=node's id, 1=parent's id, 2=node's rank
          for line in f0.readlines():
            n = line.split('|') 
            txrank[n[0].strip()] =  {
              'parentid': n[1].strip(),
              'txtype': n[2].strip(),
              'division': n[4].strip()
            }
          
          # bulk creates taxonomy nodes
          f = open('/home/app/web/r01data/names.dmp', 'r')
          count = 0
          self.txnodes = []
          self.allnodes = {}
          for line in f.readlines():
            if self.skipline(line):
              continue
            n = line.split('|')
            # 0=txid, 1=name, 2=, 3=type
            if txrank[n[0].strip()]['division'] != '0': # division code = Bacteria
              continue
            nodetype = n[3].strip()
            if nodetype not in ['scientific name', 'type material', 'synonym']:
              print('invalid nodetype:', nodetype)
              break
            # checks for key in allnodes (name + txid = unique)
            if n[1].strip() + n[0].strip() not in self.allnodes:
              rank_ = txrank[n[0].strip()]
              nodetype = 'y' if nodetype == 'synonym' else nodetype[0]
              tx_ = TxNode(
                name = n[1].strip(),
                txid = n[0].strip(),
                nodetype = nodetype,
                txtype = rank_['txtype'],
                parentid = rank_['parentid']
              )
              self.txnodes.append(tx_)
              self.allnodes[n[1].strip() + n[0].strip()] = tx_
              # creates sciname dict
              if nodetype == 's':
                self.sciname[n[0].strip()] = tx_

          # updates all nodes to include taxonomic classification
          for n in self.txnodes:
            self.set_parents(n)
          print(f'NCBI: inserting data into db...')
          # ~ print(f'self.txnodes[0]{self.txnodes[0]} kingdom:{self.txnodes[0].cKingdom} genus:{self.txnodes[0].cGenus} species:{self.txnodes[0].cSpecies} name:{self.txnodes[0].name} txid:{self.txnodes[0].txid}')
          # ~ print(f'self.txnodes[1]{self.txnodes[1]} kingdom:{self.txnodes[1].cKingdom} genus:{self.txnodes[1].cGenus} species:{self.txnodes[1].cSpecies} name:{self.txnodes[1].name} txid:{self.txnodes[1].txid}')
          # ~ return
          
          created_nodes = []
          try:
            # Bulk create: "returns created objects as a list, in
            # the same order as provided"
            created_nodes = TxNode.objects.bulk_create(self.txnodes)
          except:
            pass # e.g. duplicate unique
          print(f'NCBI: total nodes = {len(TxNode.objects.all())}')
          # ~ txnodes = []
          
          # updates parent node
          # too time intensive
          # ~ nodes = {}
          # ~ for node in created_nodes:
            # ~ nodes[node.txid] = node
          # ~ for node in created_nodes:
            # ~ try:
              # ~ if txrank[node.txid]:
                # ~ node.parent = nodes[node.parentid]
            # ~ except:
              # ~ print(f'node w/o parent? name:{node.name} txid:{node.txid} txtype:{node.txtype} parentid:{node.parentid}')
          # ~ TxNode.objects.bulk_update(created_nodes, ['parent'])
            
        except FileNotFoundError:
          print('NCBI: NCBI data files not found')
          pass
        
    except Exception as e:
      print('ncbi: waiting for Apps to be ready...', e)
      pass
      
    
      
    

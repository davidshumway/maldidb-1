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
      
  def ready(self):
    '''Checks for and installs ncbi.
    '''
    try:
      from .models import TxNode
      print('NCBI: checking NCBI...', len(TxNode.objects.all()[0:1]))
      # ~ TxNode.objects.all().delete()
      if len(TxNode.objects.all()[0:1]) < 1:
        print('NCBI: not imported, attempting to install')
        try:
          f = open('/home/app/web/r01data/names.dmp', 'r')
          count = 0
          txnodes = []
          allnodes = {}
          for line in f.readlines():
            if skipline(line):
              continue
            n = line.split('|')
            nodetype = n[3].strip()
            if nodetype not in ['scientific name', 'type material']:
              print('invalid nodetype:', nodetype)
              break
            # checks for key in allnodes
            if n[1].strip() + n[0].strip() not in allnodes:
              allnodes[n[1].strip() + n[0].strip()] = True
              txnodes.append(TxNode(
                name = n[1].strip(),
                txid = n[0].strip(),
                nodetype = nodetype[0]
              ))
            count += 1
            if count % 200000 == 0:
              try:
                TxNode.objects.bulk_create(txnodes)
              except:
                  pass # e.g. duplicate unique
              print(f'NCBI: total nodes = {len(TxNode.objects.all())}')
              txnodes = []
          # inserts final set of nodes
          TxNode.objects.bulk_create(txnodes)
          print(f'NCBI: total nodes (final) = {len(TxNode.objects.all())}')
        except FileNotFoundError:
          print('NCBI: NCBI data files not found')
          pass
        
    except Exception as e:
      print('ncbi: waiting for Apps to be ready...', e)
      pass
      
    
      
    

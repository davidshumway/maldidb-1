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

from spectra.wsviews import *
  
clients = {}

class DashConsumer(AsyncJsonWebsocketConsumer):
  
  async def connect(self):
    self.client_id = str(uuid.uuid4())
    clients[self.client_id] = self
    self.groupname = 'dashboard'
    await self.channel_layer.group_add(
      self.groupname,
      self.channel_name,
    )
    await self.accept()
    await self.send_json({'data': {'client': self.client_id}})

  async def disconnect(self, close_code):
    await self.channel_layer.group_discard(
      self.groupname,
      self.channel_name
    )

  async def receive(self, text_data):
    '''
    '''
    try:
      val = json.loads(text_data)
    except Exception as e:
      print(e)
      return
    
    if 'type' not in val:
      return
    
    # client: lib-compare
    if val['type'] == 'library comparison':
      cosine_score_libraries(self, val, self.client_id)
    # tells client result
    if val['type'] == 'library comparison result':
      d = json.dumps(val)
      await clients[val['data']['client']].send(text_data = d)
      
    # client: search existing
    if val['type'] == 'search existing':
      cosine_scores_existing(self, val['existingLibrary'],
        self.client_id, val['searchLibrary'])
    # client: full data of single score
    if val['type'] == 'single score':
      single_score(self, self.client_id, val)
    # tells client single score result
    if val['type'] == 'single score result':
      d = json.dumps({
        'data': {
          'message': 'single score result',
          'data': val['data']
        }
      })
      await clients[val['data']['client']].send(text_data = d)
      
    ## file upload ##
    
    # tells client preprocessing is complete
    if val['type'] == 'completed preprocessing':
      d = json.dumps({
        'data': {
          'message': 'completed preprocessing',
          'count': val['data']['count']
        }
      })
      await clients[val['data']['client']].send(text_data = d)
    
    # client asks to apply csv metadata
    if val['type'] == 'apply csv metadata':
      apply_csv_metadata(self, val['csv_ids'], val['library_id'])
    # tells client metadata applied
    if val['type'] == 'completed apply csv metadata':
      d = json.dumps({
        'data': {
          'message': 'completed apply csv metadata'
        }
      })
      await clients[val['data']['client']].send(text_data = d)
      
    # client asks to collapse library
    if val['type'] == 'collapse library':
      collapse_lib(self, val['collapseLibrary'], self.client_id,
        val['searchLibrary'])
    # tells client collapse completed
    if val['type'] == 'completed collapsing':
      d = json.dumps({
        'data': {
          'message': 'completed collapsing',
          'data': val['data']
        }
      })
      await clients[val['data']['client']].send(text_data = d)
      
    # tells client cosine completed
    if val['type'] == 'completed cosine':
      d = json.dumps({
        'data': {
          'message': 'completed cosine',
          'data': val['data']
        }
      })
      await clients[val['data']['client']].send(text_data = d)
    
    ## ncbi alignment ##
    
    # client asks for alignment
    if val['type'] == 'align':
      align(self, val, self.client_id)
    # send align status update
    if val['type'] == 'align status':
      d = json.dumps({
        'data': {
          'message': 'align status',
          'data': val['data']
        }
      })
      await clients[val['data']['client']].send(text_data = d)
    # sends back alignment data
    if val['type'] == 'completed align':
      d = json.dumps({
        'data': {
          'message': 'completed align',
          'data': val['data']
        }
      })
      await clients[val['data']['client']].send(text_data = d)
    # client saves alignment
    if val['type'] == 'save align':
      save_align(self, val, self.client_id)
    # sends save alignment success
    if val['type'] == 'completed save align':
      d = json.dumps({
        'data': {
          'message': 'completed save align',
          'data': val['data']
        }
      })
      await clients[val['data']['client']].send(text_data = d)
    # client asks for manual alignment
    if val['type'] == 'manual_align':
      manual_align(self, val, self.client_id)
    # sends manual alignment success
    if val['type'] == 'completed manual align':
      d = json.dumps({
        'data': {
          'message': 'completed manual align',
          'data': val['data']
        }
      })
      await clients[val['data']['client']].send(text_data = d)
    # client asks to save manual alignment
    if val['type'] == 'save manual align':
      save_manual_align(self, val, self.client_id)
    # sends save manual alignment success
    if val['type'] == 'completed save manual align':
      d = json.dumps({
        'data': {
          'message': 'completed save manual align',
          'data': val['data']
        }
      })
      await clients[val['data']['client']].send(text_data = d)
      
  async def deprocessing(self, event):
    print('==================')
    # ~ await self.send(text_data = json.dumps(event['value']))




  

  

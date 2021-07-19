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
    
    await self.send_json({'data': {'client': self.client_id}})

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
    
    # client: lib-compare
    try:
      if val['type'] == 'library comparison':
        cosine_score_libraries(self, val, self.client_id)
    except Exception as e:
      print(e)
      pass
    # tells client result
    try:
      if val['type'] == 'library comparison result':
        d = json.dumps(val)
        await clients[val['data']['client']].send(text_data = d)
    except Exception as e:
      print(e)
      pass
      
    # client: search existing
    try:
      if 'existingLibrary' in val and 'searchLibrary' in val:
        cosine_scores_existing(self, val['existingLibrary'],
          self.client_id, val['searchLibrary'])
    except Exception as e:
      print(e)
      pass
    # client: full data of single score
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




  

  

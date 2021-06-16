from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer
import json
import requests
from chat.models import Library
from mdb.utils import *

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

class DashConsumer(AsyncJsonWebsocketConsumer):

  async def connect(self):
    print('==================1')
    
    #print(f'self.scope{self.scope}')
    ip = self.scope['client'][0] + ':' + str(self.scope['client'][1])
    print(f'ip{ip}')
    #self.pusher = await self.get_pusher(ip)
    #print(self.pusher)
    
    self.groupname = 'dashboard'
    await self.channel_layer.group_add(
      self.groupname,
      self.channel_name,
    )
    await self.accept()
    
    # ~ await self.send(text_data = json.dumps({"testing from py": True}))
    await self.send_json({'data': {'ip': ip}})

  async def disconnect(self, close_code):
    print('==================2')
    await self.channel_layer.group_discard(
      self.groupname,
      self.channel_name
    )

  async def receive(self, text_data):
    '''
    Can be used to send from Python back to JS.
    '''
    print('==================3')
    # ~ #datapoint = json.loads(text_data)
    # ~ #val = datapoint['value']
    val = text_data
    
    await self.channel_layer.group_send(
      self.groupname,
      {
        'type': 'deprocessing', #function name to run
        'value': val #value to send function
      }
    )
    print ('>>>>', text_data)
    
    try:
      val = json.loads(val)
      print(f'val{val}')
      print(f'val["collapseLibrary"]{val["collapseLibrary"]}')
      if val['collapseLibrary'] != '':
        collapse_lib(self, val['collapseLibrary'])
    except Exception as e:    
      print(e)
      pass
      
  async def deprocessing(self, event):
    print('==================4')
    # send for frontend
    await self.send(text_data = json.dumps(event['value']))

@start_new_thread
def collapse_lib(self, title):
  # ~ print(f'self{self}')
  l = Library.objects.filter(title__exact = title,
    created_by = self.scope['user']).first()
  print(f'l{l}')
  if l:
    data = {
      'id': l.id,
      'owner': self.scope['user'].id
    }
    print(f'data{data}')
    r = requests.get(
      'http://plumber:8000/collapseLibrary',
      params = data
    )
    print(f'r{r}')

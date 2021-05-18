from channels.generic.websocket import AsyncJsonWebsocketConsumer

from channels.generic.websocket import WebsocketConsumer

import json

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
  print('==================0')
  async def connect(self):
    print('==================1')
    self.groupname = 'dashboard'
    await self.channel_layer.group_add(
      self.groupname,
      self.channel_name,
    )
    await self.accept()

  async def disconnect(self, close_code):
    print('==================2')
    await self.channel_layer.group_discard(
      self.groupname,
      self.channel_name
    )

  async def receive(self, text_data):
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

  async def deprocessing(self, event):
    print('==================4')
    valOther = event['value']
    valOther = f'VALUE: {valOther}'
    # send for frontend
    await self.send(text_data = json.dumps(event['value']))
    # ~ await self.send(text_data = json.dumps({'value2': valOther}))

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from chat import consumer

# ~ from .wsgi import *

# ~ websocket_urlPattern = [
	# ~ # In routing.py, "as_asgi()" is required for versions over python 3.6.
	# ~ path('ws/pollData', consumer.DashConsumer),
	# ~ path('ws/pollData', consumer.DashConsumer.as_asgi()),
# ~ ]
# ~ application = ProtocolTypeRouter({
  # ~ 'http': get_asgi_application(),
  # ~ 'websocket': AuthMiddlewareStack(
    # ~ URLRouter(websocket_urlPattern) 
  # ~ )
# ~ })
# ~ application = ProtocolTypeRouter({
  # ~ 'websocket': AuthMiddlewareStack(
    # ~ URLRouter(websocket_urlPattern) 
  # ~ )
# ~ })

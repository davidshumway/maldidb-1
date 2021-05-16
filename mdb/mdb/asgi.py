"""
ASGI config for djangoproject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

# ~ import os
# ~ import django
# ~ from django.core.asgi import get_asgi_application
# ~ from channels.routing import get_default_application
# ~ os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mdb.settings')
# ~ django.setup()
# ~ application = get_default_application()

# ~ import os
# ~ from django.core.asgi import get_asgi_application
# ~ os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mdb.settings')
# ~ application = get_asgi_application()





import os
from django.conf.urls import url
from django.core.asgi import get_asgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mdb.settings")
django_asgi_app = get_asgi_application()
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from chat.consumer import DashConsumer
application = ProtocolTypeRouter({
  "http": django_asgi_app,
  "websocket": AuthMiddlewareStack(
    URLRouter([
      url(r"^ws/pollData$", DashConsumer.as_asgi()),
    ])
  ),
})




# ~ import os
# ~ os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mdb.settings')
# ~ import django
# ~ django.setup()
# ~ from channels.routing import get_default_application
# ~ from django.core.asgi import get_asgi_application
# ~ from channels.routing import ProtocolTypeRouter, URLRouter
# ~ from channels.auth import AuthMiddlewareStack
# ~ from django.urls import path
# ~ from chat import consumer

# ~ application = ProtocolTypeRouter({
  # ~ 'http': get_asgi_application(),
  #'http': get_default_application(),
  # ~ 'websocket': AuthMiddlewareStack(
    # ~ URLRouter([
      #path('ws/pollData', consumer.DashConsumer),
      # ~ path('ws/pollData', consumer.DashConsumer.as_asgi()),
    # ~ ])
  # ~ )
# ~ })

# ~ import os
# ~ from channels.auth import AuthMiddlewareStack
# ~ from channels.routing import ProtocolTypeRouter, URLRouter
# ~ from django.core.asgi import get_asgi_application
# ~ import mdb.routing
# ~ os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mdb.settings")
# ~ application = ProtocolTypeRouter({
  # ~ "http": get_asgi_application(),
  # ~ "websocket": AuthMiddlewareStack(
    # ~ URLRouter(
      # ~ mdb.routing.websocket_urlpatterns
    # ~ )
  # ~ ),
# ~ })

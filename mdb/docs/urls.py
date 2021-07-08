from django.urls import path, include
from . import views
app_name = 'docs'

urlpatterns = [
  path('', views.docs, name='docs'),
]

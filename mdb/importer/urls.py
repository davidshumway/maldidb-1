from django.urls import path, re_path, include
from . import views
app_name = 'importer'
urlpatterns = [ # import/
  # Ex. /import/sqlite/
  path('sqlite/', views.add_sqlite, name = 'add_sqlite'),
]

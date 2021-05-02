from django.urls import path, re_path, include
from . import views
app_name = 'spectra'

urlpatterns = [

  path('', views.add_post, name='add_post'),
  path('data/add', views.add_post, name='add_post'),
  path('spectra/<spectra_id>/', views.spectra_profile, name='view_spectra'),
  path('spectra/edit/<spectra_id>/', views.edit_spectra, name='edit_spectra'),
  
]

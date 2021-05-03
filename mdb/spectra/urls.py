from django.urls import path, re_path, include
from . import views
app_name = 'spectra'

from rest_framework.routers import SimpleRouter
from .views import SpectraViewSet
from .views import CollapsedSpectraViewSet
router = SimpleRouter()
router.register('s', SpectraViewSet)
router.register('cs', CollapsedSpectraViewSet)

urlpatterns = [

  path('', views.SpectraListView.as_view(), name='home'),
  path('data/add', views.add_post, name='add_post'),
  path('spectra/<spectra_id>/', views.spectra_profile, name='view_spectra'),
  path('spectra/edit/<spectra_id>/', views.edit_spectra, name='edit_spectra'),
  
] + router.urls

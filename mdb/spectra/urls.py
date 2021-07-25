from django.urls import path, re_path, include
from . import views
app_name = 'spectra'

from rest_framework.routers import SimpleRouter
from .views import SpectraViewSet
from .views import CollapsedSpectraViewSet
from .views import CollapsedCosineScoreViewSet
router = SimpleRouter()
router.register('s', SpectraViewSet)
router.register('cs', CollapsedSpectraViewSet)
router.register('ccs', CollapsedCosineScoreViewSet)

urlpatterns = [

  path('', views.SpectraListView.as_view(), name='home'),
  path('data/add', views.add_post, name='add_post'),
  path('spectra/<spectra_id>/', views.spectra_profile, name='view_spectra'),
  path('spectra2/<spectra_id>/', views.spectra2_profile, name='view_spectra2'),
  path('spectra/edit/<spectra_id>/', views.edit_spectra, name='edit_spectra'),
  path('lib-compare/', views.lib_compare, name='lib_compare'),
  path('lib-compare/<library_ids>/', views.lib_compare2, name='lib_compare2'),
  
] + router.urls

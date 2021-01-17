""" soMedia URL Configuration """

from django.urls import path
from . import views
from .views import SearchResultsView, LibrariesListView, SpectraListView
from .views import MetadataListView, LabgroupsListView, XmlListView
from .views import FilteredSpectraListView, FilteredSpectraSearchListView
# ~ from .views import PersonList

app_name = 'chat'
urlpatterns = [
    path('', views.home, name='home'),
    path('cosine/', views.view_cosine, name='view_cosine'),
    
    path('data/add', views.add_post, name='add_post'),
    path('data/add_metadata', views.add_metadata, name='add_metadata'),
    path('data/add_sqlite', views.add_sqlite, name='add_sqlite'),
    path('data/add_lib', views.add_lib, name='add_lib'),
    path('data/add_labgroup', views.add_labgroup, name='add_labgroup'),
    path('data/add_xml', views.add_xml, name='add_xml'),
    
    path('comments/add/<post_id>', views.add_comment, name='add_comment'),
    
    # ~ path('search/', views.search, name='search'),
    # ~ path('search/', SearchResultsView.as_view(), name='search_results'),
    
    
    # basic / advanced search
    # ~ path('test/', PersonList.as_view(), name='testxyz'),
    path('search/', FilteredSpectraSearchListView.as_view(), name='basic_search'),
    # ~ path('search/', FilteredSpectraListView.as_view(), name='search_results'),
    
    path('libraries/', LibrariesListView.as_view(), name='libraries_results'),
    
    # ~ path('spectra/', SpectraListView.as_view(), name='spectra_results'),
    path('spectra/', FilteredSpectraListView.as_view(), name='spectra_results'),
    
    # All spectra from a library / filter
    # ~ path('spectra/<library_id/', FilteredSpectraLibListView.as_view(), name='spectra_library_results'),
    
    path('metadata/', MetadataListView.as_view(), name='metadata_results'),
    path('metadata/<strain_id>/', views.metadata_profile, name='view_metadata'),
    path('metadata/edit/<strain_id>/', views.edit_metadata, name='edit_metadata'),
    
    path('labgroups/', LabgroupsListView.as_view(), name='labgroups_results'),
    #test
    
    path('xml/', XmlListView.as_view(), name='xml_results'),
    path('xml/<xml_hash>/', views.xml_profile, name='view_xml'),
    path('xml/edit/<xml_hash>/', views.edit_xml, name='edit_xml'),
    
    path('spectra/<spectra_id>/', views.spectra_profile, name='view_spectra'),
    path('spectra/edit/<spectra_id>/', views.edit_spectra, name='edit_spectra'),
    
    path('library/<library_id>/', views.library_profile, name='view_library'),
    path('library/edit/<library_id>/', views.edit_libprofile, name='edit_libprofile'),
    
    path('labs/<lab_id>/', views.lab_profile, name='view_lab'),
    path('labs/edit/<lab_id>/', views.edit_labprofile, name='edit_labprofile'),
    
    path('preview_collapse/lib/<lib_id>/', views.preview_collapse_lib, name='preview_collapse_lib'),
    
    
    
]

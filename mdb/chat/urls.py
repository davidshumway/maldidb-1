from django.urls import path, re_path, include
from . import views
app_name = 'chat'

urlpatterns = [
  path('', views.home, name='home'),

  path('data/add_metadata', views.add_metadata, name='add_metadata'),
  path('data/add_lib', views.add_lib, name='add_lib'),
  path('data/add_labgroup', views.add_labgroup, name='add_labgroup'),
  path('data/add_xml', views.add_xml, name='add_xml'),
  
  path('comments/add/<post_id>', views.add_comment, name='add_comment'),
  
  path('libraries/', views.LibrariesListView.as_view(), name='libraries_results'),
  
  # All spectra from a library / filter
  # ~ path('spectra/<library_id/', FilteredSpectraLibListView.as_view(), name='spectra_library_results'),
  
  path('metadata/', views.FilteredMetadataListView.as_view(), name='metadata_results'),
  path('metadata/<strain_id>/', views.metadata_profile, name='view_metadata'),
  path('metadata/edit/<strain_id>/', views.edit_metadata, name='edit_metadata'),
  
  path('labgroups/', views.LabgroupsListView.as_view(), name='labgroups_results'),
  #test
  
  path('xml/', views.XmlListView.as_view(), name='xml_results'),
  path('xml/<xml_hash>/', views.xml_profile, name='view_xml'),
  path('xml/edit/<xml_hash>/', views.edit_xml, name='edit_xml'),
  
  path('library/', views.library_profile, name='view_library_base'),
  path('library/<library_id>/', views.library_profile, name='view_library'),
  path('library/edit/<library_id>/', views.edit_libprofile, name='edit_libprofile'),
  
  path('labs/<lab_id>/', views.lab_profile, name='view_lab'),
  path('labs/edit/<lab_id>/', views.edit_labprofile, name='edit_labprofile'),
  
  path('collapse/<lib_id>/', views.collapse_library, name='collapse_library'),
  
  path('tasks/', views.UserTaskListView.as_view(), name='user_tasks'),
  
  path('statuses/<status_id>/', views.user_task_status_profile, name='user_task_statuses'),
  
  path('site_metrics/', views.site_metrics, name='site_metrics'),
  path('user_libraries/', views.user_libraries, name='user_libraries'),
  
]

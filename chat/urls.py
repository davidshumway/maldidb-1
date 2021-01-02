""" soMedia URL Configuration """

from django.urls import path
from . import views
from .views import SearchResultsView, LibrariesListView, SpectraListView, MetadataListView, LabgroupsListView


app_name = 'chat'
urlpatterns = [
    path('', views.home, name='home'),
    path('posts/add', views.add_post, name='add_post'),
    path('posts/add_metadata', views.add_metadata, name='add_metadata'),
    path('posts/add_sqlite', views.add_sqlite, name='add_sqlite'),
    path('posts/add_lib', views.add_lib, name='add_lib'),
    path('posts/add_labgroup', views.add_labgroup, name='add_labgroup'),
    path('comments/add/<post_id>', views.add_comment, name='add_comment'),
    path('search/', SearchResultsView.as_view(), name='search_results'),
    path('libraries/', LibrariesListView.as_view(), name='libraries_results'),
    path('spectra/', SpectraListView.as_view(), name='spectra_results'),
    path('metadata/', MetadataListView.as_view(), name='metadata_results'),
    path('labgroups/', LabgroupsListView.as_view(), name='labgroups_results'),
    #test
]

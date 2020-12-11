""" soMedia URL Configuration """

from django.urls import path
from . import views
from .views import SearchResultsView
from .views import LibrariesListView


app_name = 'chat'
urlpatterns = [
    path('', views.home, name='home'),
    path('posts/add', views.add_post, name='add_post'),
    path('posts/add_metadata', views.add_metadata, name='add_metadata'),
    path('posts/add_sqlite', views.add_sqlite, name='add_sqlite'),
    path('posts/add_lib', views.add_lib, name='add_lib'),
    path('comments/add/<post_id>', views.add_comment, name='add_comment'),
    path('search/', SearchResultsView.as_view(), name='search_results'),
    path('libraries/', LibrariesListView.as_view(), name='libraries_results'),
    #test
]

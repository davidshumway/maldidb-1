from django.urls import path, include
from . import views

app_name = 'files'
urlpatterns = [
  path('', views.UserFilesListView.as_view(), name='user_files'),
]

from django.urls import path, include
from . import views

app_name = 'files'
urlpatterns = [
  path('', views.UserFilesListView.as_view(), name='user_files'),
  path('file-upload/', views.FileUpload.as_view(), name='file_upload'),
  # ~ path('file-upload/', views.file_upload, name='file_upload'),
]

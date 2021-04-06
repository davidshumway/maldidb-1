from django.shortcuts import render
from .models import UserFile
from django_tables2 import SingleTableView
from .tables import *

class UserFilesListView(SingleTableView):
  model = UserFile
  table_class = UserFileTable
  template_name = 'files/user_files.html'
  
  def get_queryset(self, *args, **kwargs):
    return UserFile.objects.filter(owner = self.request.user) \
      .order_by('-upload_date') #last_modified

from django.shortcuts import render
from .models import UserFile
from django_tables2 import SingleTableView
from .tables import *
from .forms import *
from django.views.generic.list import ListView

class UserFilesListView(SingleTableView):
  model = UserFile
  table_class = UserFileTable
  template_name = 'files/user_files.html'
  
  def get_queryset(self, *args, **kwargs):
    return UserFile.objects.filter(owner = self.request.user) \
      .order_by('-upload_date') #last_modified

class FileUpload(ListView):
  model = UserFile
  template_name = 'files/file_upload.html'
  
  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['upload_form'] = FileUploadForm()
    u = self.request.user
    
    # own libraries (library_select shares this qs)
    q = Library.objects.filter(created_by__exact = u)
    context['upload_form'].fields['library_select'].queryset = q
    
    return context

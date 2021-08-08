from django.shortcuts import render
from .models import *
from .tables import *
from django_tables2 import SingleTableView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name = 'dispatch')
class UserTaskListView(SingleTableView):
  model = UserTask
  table_class = UserTaskTable
  template_name = 'tasks/user_tasks.html'
  
  def get_queryset(self, *args, **kwargs):
    return UserTask.objects.filter(owner = self.request.user) \
      .order_by('-last_modified') #statuses__status_date

@login_required
def user_task_status_profile(request, status_id):
  uts = UserTaskStatus.objects.get(id = status_id)
  return render(
    request,
    'tasks/user_task_status_profile.html',
    {'user_task_status': uts}
  )

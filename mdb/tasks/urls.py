from django.urls import path, re_path, include
from . import views
app_name = 'tasks'

urlpatterns = [
  #path('', views.home, name='home'),

  path('tasks/', views.UserTaskListView.as_view(), name='user_tasks'),
  path('statuses/<status_id>/', views.user_task_status_profile, name='user_task_statuses'),
  
]

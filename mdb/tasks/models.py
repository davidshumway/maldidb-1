from django.db import models
from django.conf import settings

class UserTask(models.Model):
  '''
  '''
  owner = models.ForeignKey( # Empty owner implies anonymous user
    settings.AUTH_USER_MODEL,
    on_delete = models.CASCADE,
    blank = True,
    null = True)
  task_choices = [
    ('idbac_sql', 'Insert IDBac SQLite data to database'),
    ('spectra', 'Add spectra files to database'),
    ('preprocess', 'Preprocess spectra'),
    ('collapse', 'Collapse replicates'),
    ('cos_search', 'Cosine score search'),
    ('metadata', 'Add metadata'),
  ]
  task_description = models.CharField(
    max_length = 255,
    choices = task_choices,
    blank = True,
    null = True
  )
  statuses = models.ManyToManyField('UserTaskStatus')
  last_modified = models.DateTimeField(auto_now_add = True, blank = False)
 
class UserTaskStatus(models.Model):
  '''Describe lifecycle events of user tasks.
  
  -- An extra field to optionally further explain the status.
  -- Each time a new status is created, trigger last_modified on UserTask
     to update.
  -- @user_task: FK, Link back to UserTask containing this status (m2m)
  '''
  status_choices = [
    ('start', 'Started'),
    ('run', 'Running'),
    ('complete', 'Completed'),
    ('error', 'Completed - Error'),
    ('info', 'Info') # a status to report task progress
  ]
  status = models.CharField(
    max_length = 255,
    choices = status_choices,
    blank = False,
    null = False
  )
  status_date = models.DateTimeField(auto_now_add = True, blank = False)
  extra = models.TextField(blank = True, null = True)
  user_task = models.ForeignKey(
    'UserTask',
    # ~ related_name = '',
    on_delete = models.CASCADE,
    blank = True, null = True)

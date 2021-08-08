from threading import Thread
from tasks.models import UserTask, UserTaskStatus
import requests

def start_new_thread(function):
  '''Starts a new thread for long-running tasks'''
  def decorator(*args, **kwargs):
    t = Thread(target = function, args = args, kwargs = kwargs)
    t.daemon = True
    t.start()
    return t
  return decorator

class BgProcess:
  
  def __init__(self):
    pass
  
  @classmethod
  def collapse_lib(cls, id, owner):
    t = UserTask.objects.create(
      owner = owner,
      task_description = 'collapse'
    )
    t.statuses.add(UserTaskStatus.objects.create(status = 'start'))
    cls.collapse_lib_thread(id, owner.id, t)
  
  @start_new_thread
  def collapse_lib_thread(id, owner, task):
    data = {'id': id, 'owner': owner}
    r = requests.get('http://plumber:8000/collapseLibrary', params = data)
    if r.status_code < 300:
      task.statuses.add(UserTaskStatus.objects.create(status = 'complete'))
    else:
      task.statuses.add(UserTaskStatus.objects.create(
        status = 'error',
        extra = r.content
      ))

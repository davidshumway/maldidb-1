from threading import Thread

def start_new_thread(function):
  '''Starts a new thread for long-running tasks'''
  def decorator(*args, **kwargs):
    t = Thread(target = function, args = args, kwargs = kwargs)
    t.daemon = True
    t.start()
    return t
  return decorator

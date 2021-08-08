import django_tables2 as tables
from .models import *
from django.urls import reverse
from django.utils.html import format_html, format_html_join, html_safe, escape
import re

class UserTaskTable(tables.Table):
  '''
  '''
  statuses = tables.ManyToManyColumn(
    # ~ transform = lambda s: s.status,
    # ~ separator = '---***---***---***---'
  )
  
  def render_statuses(self, value):
    '''
    
    For some reason format_html does not like extraneous curly braces?
    '''
    out = []
    for s in value.all():
      r = s.status + ' (' + str(s.status_date) + ')'
      if s.extra != '' and s.extra != None:
        s.extra = s.extra[0:40] + '...' if s.extra != None and len(s.extra) > 40 else s.extra
        n = reverse('tasks:user_task_statuses', args=(s.id, ))
        c = 'info' if s.status == 'info' else 'danger'
        r += format_html(
          '<div class="alert alert-{}"><a href="{}">{}</a></div>',
          c, n, re.sub(r'[\{\}]', '', s.extra))
      out.append(r)
    return format_html("<br>".join(out))
    
  class Meta:
    model = UserTask
    attrs = {"class": "table maintable"}
    template_name = "chat/bootstrap4_mod.html"
    exclude = ('id', 'owner')

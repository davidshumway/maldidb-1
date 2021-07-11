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
    
    For some reason format_html does not like extraneous curly braces??
    '''
    out = []
    for s in value.all():
      r = s.status + ' (' + str(s.status_date) + ')'
      if s.extra != '' and s.extra != None:
        s.extra = s.extra[0:40] + '...' if s.extra != None and len(s.extra) > 40 else s.extra
        n = reverse('chat:user_task_statuses', args=(s.id, ))
        c = 'info' if s.status == 'info' else 'danger'
        r += format_html(
          '<div class="alert alert-{}"><a href="{}">{}</a></div>',
          c, n, re.sub(r'[\{\}]', '', s.extra))
      out.append(r)
    return format_html("<br>".join(out))
  
  # ~ def __init__(self, *args, **kwargs):
    # ~ '''Default order is newest task descending'''
    # ~ print(f'utt args {args}')
    # ~ print(f'utt kwargs {kwargs}')
    # ~ if kwargs.get('data'):
      # ~ d = kwargs.pop('data', None)
      # ~ self.testing_data = d.get('scores', None)
      # ~ kwargs.setdefault('data', d.get('queryset', None))
    # ~ super().__init__(*args, **kwargs)
    
  class Meta:
    model = UserTask
    attrs = {"class": "table maintable"}
    template_name = "chat/bootstrap4_mod.html"
    exclude = ('id', 'owner')
  
class LibCollapseTable(tables.Table):
  num_replicates = tables.Column()
  strain_id = tables.Column()
  # ~ spectrum_type = tables.Column()
  
  def render_strain_id(self, value):
    # ~ print('rsid value', value)
    # ~ return '-----'+value.strain_id
    return value
    
  class Meta:
    model = Spectra
    attrs = {"class": "table maintable"}
    template_name = "chat/bootstrap4_mod.html"
    fields = ['strain_id']
    
class XmlTable(tables.Table):
  created_by = tables.Column(linkify=True)
  lab = tables.Column(linkify=True)
  xml_hash = tables.Column(linkify=True)
  selector = tables.CheckBoxColumn()
  
  class Meta:
    model = XML
    attrs = {"class": "table maintable"}
    template_name = "chat/bootstrap4_mod.html"
    exclude = ('id','xml') # xml too large to show
    sequence = ('selector', '...')
    
class LibraryTable(tables.Table):
  # ~ created_by = tables.Column(linkify = True)
  lab = tables.Column(linkify = True)
  title = tables.Column(linkify = True)
  # ~ collapse_replicates = tables.Column(accessor = 'id',
    # ~ verbose_name = 'Collapse Replicates')
  # ~ selector = tables.CheckBoxColumn(accessor = 'id')
  
  # ~ def render_collapse_replicates(self, value):
    # ~ r = reverse('chat:collapse_library', args = [str(value)])
    # ~ return format_html(
      # ~ '<a href="{}">collapse</a>', r
    # ~ )
    
  class Meta:
    model = Library
    attrs = {'class': 'table maintable'}
    template_name = 'chat/bootstrap4_mod.html'
    exclude = ('id', 'created_by')
    sequence = ('title', 'lab', '...')
    # ~ sequence = ('selector', '...')

class MetadataTable(tables.Table):
  class Meta:
    model = Metadata
    attrs = {'class': 'table maintable'}
    template_name = 'chat/bootstrap4_mod.html'
    exclude = ('id',)

class LabgroupTable(tables.Table):
  lab_name = tables.Column(linkify=True)
  owners = tables.ManyToManyColumn(accessor = 'owners',
    verbose_name = 'Num. owners'
  )
  members = tables.ManyToManyColumn(accessor = 'members',
    verbose_name = 'Num. members'
  )
  # TODO: link to lab libraries
  # TODO: number of lab libraries
  
  def render_owners(self, value):
    '''
    '''
    return len(value.all())
  def render_members(self, value):
    '''
    '''
    return len(value.all())
    
  class Meta:
    model = LabGroup
    attrs = {'class': 'table maintable'}
    template_name = 'chat/bootstrap4_mod.html'
    exclude = ('id',)

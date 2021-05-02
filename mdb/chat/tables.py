import django_tables2 as tables
from .models import *
from django.urls import reverse
from django.utils.html import format_html, format_html_join, html_safe

# ~ class UserLogsTable(tables.Table):
  # ~ class Meta:
    # ~ model = UserLogs
    # ~ attrs = {"class": "table maintable"}
    # ~ template_name = "chat/bootstrap4_mod.html"
    # ~ exclude = ('id',)
      
class UserTaskTable(tables.Table):
  '''
  -- friends = tables.ManyToManyColumn(transform=lambda user: u.name)
  If only the active friends should be displayed, you can use the `filter` argument::
  friends = tables.ManyToManyColumn(filter=lambda qs: qs.filter(is_active=True))
  '''
  statuses = tables.ManyToManyColumn(
    # ~ transform = lambda s: s.status,
    # ~ separator = '---***---***---***---'
  )
  
  def render_statuses(self, value):
    out = []
    for s in value.all():
      r = s.status + ' (' + str(s.status_date) + ')'
      if s.extra != '':
        s.extra = s.extra[0:40] + '...' if s.extra != None and len(s.extra) > 40 else s.extra
        n = reverse('chat:user_task_statuses', args=(s.id, ))
        c = 'info' if s.status == 'info' else 'danger'
        r += format_html(
          '<div class="alert alert-{}"><a href="{}">{}</a></div>',
          c, n, s.extra)
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
  lab_name = tables.Column(linkify=True)
  xml_hash = tables.Column(linkify=True)
  selector = tables.CheckBoxColumn()
  
  class Meta:
    model = XML
    attrs = {"class": "table maintable"}
    template_name = "chat/bootstrap4_mod.html"
    exclude = ('id','xml') # xml too large to show
    sequence = ('selector', '...')
    
class LibraryTable(tables.Table):
  created_by = tables.Column(linkify = True)
  lab_name = tables.Column(linkify = True)
  title = tables.Column(linkify = True)
  #test = tables.CheckBoxColumn(accessor='test')
  collapse_replicates = tables.Column(accessor = 'id',
    verbose_name = 'Collapse Replicates')#, linkify=True)
  selector = tables.CheckBoxColumn(accessor = 'id')
  
  def render_collapse_replicates(self, value):
    # pass lib_id
    r = reverse('chat:preview_collapse_lib') #, args=(value, )
    return format_html(
      '<a href="{}?library='+str(value)+'">preview</a>', r
    )
    
  class Meta:
    model = Library
    attrs = {'class': 'table maintable'}
    template_name = 'chat/bootstrap4_mod.html'
    exclude = ('id',)
    sequence = ('selector', '...')

class MetadataTable(tables.Table):
  class Meta:
    model = Metadata
    attrs = {"class": "table maintable"}
    template_name = "chat/bootstrap4_mod.html"
    exclude = ("id",)

class LabgroupTable(tables.Table):
  lab_name = tables.Column(linkify=True)
  class Meta:
    model = LabGroup
    attrs = {"class": "table maintable"}
    template_name = "chat/bootstrap4_mod.html"
    exclude = ("id",)

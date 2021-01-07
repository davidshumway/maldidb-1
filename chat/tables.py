import django_tables2 as tables
from .models import Library, Spectra, Metadata, LabGroup, SearchSpectraCosineScore

class LibraryTable(tables.Table):
  created_by = tables.Column(linkify=True)
  lab_name = tables.Column(linkify=True)
  title = tables.Column(linkify=True)
  #test = tables.CheckBoxColumn(accessor='test')
  class Meta:
    model = Library
    attrs = {"class": "table maintable"}
    template_name = "django_tables2/bootstrap4.html"
    exclude = ("id",)

class CosineSearchTable(tables.Table):
  
  # Provide verbose name for score, otherwise it defaults to ID
  score = tables.Column(accessor='id', verbose_name='Score')
  
  testing_data = None
  
  def render_strain_id(self, value):
    return value.strain_id
    
  def render_score(self, record):
    '''
    record: entire record for the row from the table data
    '''
    print('render_score:', record)
    # ~ print('bc',bound_column)
    # ~ return ''
    return self.testing_data.get(record.id)#'++++'
    # ~ return self.testing_data.get(str(record.id))#'++++'
  
  def __init__(self, *args, **kwargs):
    '''generate the scores here
    then each row can access them.
    '''
    #
    # ~ d = kwargs.get('data')
    
    d = kwargs.pop('data', None)
    # ~ print(f'-d: {d}' )
    self.testing_data = d.get('scores')
    kwargs.setdefault('data', d.get('queryset'))
    
    # ~ ex = []
    # ~ for obj in d:
      # ~ ex.append(('scores',tables.Column()))
    # ~ kwargs.update({
      # ~ 'extra_columns': ex
    # ~ })


    # ~ '''
    # ~ kwargs: {'data': <QuerySet [<Spectra..>, <Spectra..>, ...]>}
    # ~ becomes
    # ~ kwargs: {'data': {'extra': '12345', ...}
    # ~ '''
    # ~ # print('args', *args) # none
    # ~ print(f'-args: {args}' ) # prints: 
    # ~ print(f'-kw: {kwargs}' ) # prints: kw: {'data': <QuerySet [<Spectra..>, <Spectra..>, ...]>}
    # ~ # d = kwargs.pop('data', None)
    # ~ # kwargs.setdefault('data', d.get('queryset'))
    super().__init__(*args, **kwargs)
    

  class Meta:
    model = Spectra
    attrs = {"class": "table maintable"}
    template_name = "chat/bootstrap4_mod.html"
    exclude = ()#'spectra1')
    sequence = ('score', 'strain_id', '...')

class SpectraTable(tables.Table):
  created_by = tables.Column(linkify=True)
  lab_name = tables.Column(linkify=True)
  library = tables.Column(linkify=True)
  id = tables.Column(linkify=True)
  class Meta:
    model = Spectra
    attrs = {"class": "table maintable"}
    template_name = "chat/bootstrap4_mod.html"
    # ~ exclude = ("id",)
    exclude = ()

class MetadataTable(tables.Table):
  class Meta:
    model = Metadata
    attrs = {"class": "table maintable"}
    template_name = "django_tables2/bootstrap4.html"
    exclude = ("id",)

class LabgroupTable(tables.Table):
  lab_name = tables.Column(linkify=True)
  class Meta:
    model = LabGroup
    attrs = {"class": "table maintable"}
    template_name = "django_tables2/bootstrap4.html"
    exclude = ("id",)

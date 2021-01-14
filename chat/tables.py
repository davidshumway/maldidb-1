import django_tables2 as tables
from .models import Library, Spectra, Metadata, LabGroup, SearchSpectraCosineScore, XML

class XmlTable(tables.Table):
  created_by = tables.Column(linkify=True)
  lab_name = tables.Column(linkify=True)
  xml_hash = tables.Column(linkify=True)
  # ~ title = tables.Column(linkify=True)
  #test = tables.CheckBoxColumn(accessor='test')
  class Meta:
    model = XML
    attrs = {"class": "table maintable"}
    template_name = "chat/bootstrap4_mod.html"
    exclude = ('id','xml') # xml too large to show
    
class LibraryTable(tables.Table):
  created_by = tables.Column(linkify=True)
  lab_name = tables.Column(linkify=True)
  title = tables.Column(linkify=True)
  #test = tables.CheckBoxColumn(accessor='test')
  class Meta:
    model = Library
    attrs = {"class": "table maintable"}
    template_name = "chat/bootstrap4_mod.html"
    exclude = ("id",)

class CosineSearchTable(tables.Table):
  '''
  Provide verbose name for score, otherwise defaults to "ID" on render.
  '''
  
  score = tables.Column(accessor='id', verbose_name='Score')
  id = tables.Column(linkify=True)
  xml_hash = tables.Column(linkify=True)
  
  # Abbreviate col. names
  strain_id = tables.Column(linkify=True, verbose_name='Strain ID')
  v1_tof_calibration = tables.Column(verbose_name='V1 TOF cal.')
  spectrometer_type = tables.Column(verbose_name='Spec. type')
  ionization_mode = tables.Column(verbose_name='Ion. mode')
  acquisition_mode = tables.Column(verbose_name='Acq. mode')
  # ~ tof_mode = tables.Column(verbose_name='TM')
  acquisition_operator_mode = tables.Column(verbose_name='Acq. op. mode')
  laser_attenuation = tables.Column(verbose_name='Las. att.')
  
  testing_data = {}
  
  def render_strain_id(self, value):
    return value.strain_id
  
  def render_xml_hash(self, value):
    return value.xml_hash
    
  def render_score(self, record):
    '''
    record: entire record for the row from the table data
    '''
    # ~ print('render_score:', record)
    return self.testing_data.get(record.id, None)
  
  def __init__(self, *args, **kwargs):
    '''generate the scores here
    then each row can access them.
    '''
    
    if kwargs.get('data'):
      d = kwargs.pop('data', None)
      self.testing_data = d.get('scores', None)
      kwargs.setdefault('data', d.get('queryset', None))
    
    super().__init__(*args, **kwargs)
    

  class Meta:
    model = Spectra
    attrs = {"class": "table maintable"}
    template_name = "chat/bootstrap4_mod.html"
    exclude = ('picture',)#'spectra1')
    sequence = ('id', 'score', 'strain_id', '...')
    row_attrs = {
      'valign': 'top'
    }

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
    template_name = "chat/bootstrap4_mod.html"
    exclude = ("id",)

class LabgroupTable(tables.Table):
  lab_name = tables.Column(linkify=True)
  class Meta:
    model = LabGroup
    attrs = {"class": "table maintable"}
    template_name = "chat/bootstrap4_mod.html"
    exclude = ("id",)

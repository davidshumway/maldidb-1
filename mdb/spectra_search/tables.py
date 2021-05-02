import django_tables2 as tables
from chat.models import *
from spectra.models import *
from django.urls import reverse
from django.utils.html import format_html, format_html_join, html_safe

class CosineSearchTable(tables.Table):
  '''
  Provide verbose name for score, otherwise defaults to "ID" on render.
  '''
  
  score = tables.Column(accessor='id', verbose_name='Score')
  id = tables.Column(linkify=True)
  xml_hash = tables.Column(linkify=True)
  
  # Abbreviate col. names
  strain_id = tables.Column(linkify=True, verbose_name='Strain ID')
  # ~ v1_tof_calibration = tables.Column(verbose_name='V1 TOF cal.')
  # ~ spectrometer_type = tables.Column(verbose_name='Spec. type')
  # ~ ionization_mode = tables.Column(verbose_name='Ion. mode')
  # ~ acquisition_mode = tables.Column(verbose_name='Acq. mode')
  # ~ acquisition_operator_mode = tables.Column(verbose_name='Acq. op. mode')
  # ~ laser_attenuation = tables.Column(verbose_name='Las. att.')
  
  testing_data = {}
  
  def render_strain_id(self, value):
    return value.strain_id
  
  def render_xml_hash(self, value):
    return value.xml_hash
    
  def render_score(self, record):
    '''
    record: entire record for the row from the table data
    '''
    return self.testing_data.get(record.id, None)
  
  def __init__(self, *args, **kwargs):
    '''some reworking here to get queryset and data back to table'''
    
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

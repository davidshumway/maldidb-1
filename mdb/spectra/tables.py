import django_tables2 as tables
from .models import *
from django.urls import reverse
from django.utils.html import format_html, format_html_join, html_safe

class SpectraTable(tables.Table):
  created_by = tables.Column(linkify=True)
  lab = tables.Column(linkify=True)
  library = tables.Column(linkify=True)
  id = tables.Column(linkify=True)
  selector = tables.CheckBoxColumn()
  
  class Meta:
    model = Spectra
    attrs = {'class': 'table maintable'}
    template_name = 'chat/bootstrap4_mod.html'
    exclude = ()
    sequence = ('selector','id', 'strain_id', '...')

class CollapsedSpectraTable(tables.Table):
  # ~ created_by = tables.Column(linkify=True)
  lab = tables.Column(linkify=True)
  library = tables.Column(linkify=True)
  id = tables.Column(linkify=True)
  selector = tables.CheckBoxColumn()
  #collapsed_spectra = tables.ManyToManyColumn()
  num_spectra = tables.Column()
  # ~ num_spectra = tables.ManyToManyColumn(accessor = 'collapsed_spectra',
    # ~ transform = lambda user: u.name
  # ~ )
  
  # ~ def render_collapsed_spectra(self, value):
    # ~ return value.collapsed_spectra
  
  class Meta:
    model = CollapsedSpectra
    attrs = {'class': 'table maintable'}
    template_name = 'chat/bootstrap4_mod.html'
    exclude = ()
    sequence = ('selector','id', 'strain_id', '...')

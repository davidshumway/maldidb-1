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
  # ~ created_by = tables.Column(linkify=True)
  # ~ lab_name = tables.Column(linkify=True)
  # ~ library = tables.Column(linkify=True)
  # ~ spectra1 = tables.Column(linkify=True)
  spectra2 = tables.Column(linkify=True)
  # ~ score = tables.Column()
  def render_spectra2(self, value):
    try:
      return value.strain_id.strain_id
    except:
      try:
        return value.strain_id
      except:
        return value
      
  class Meta:
    model = SearchSpectraCosineScore
    attrs = {"class": "table maintable"}
    template_name = "chat/bootstrap4_mod.html"
    exclude = ("id",'spectra1')

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

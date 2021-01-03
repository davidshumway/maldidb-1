import django_tables2 as tables
from .models import Library, Spectra, Metadata, LabGroup

class LibraryTable(tables.Table):
  class Meta:
    model = Library
    attrs = {"class": "table maintable"}
    template_name = "django_tables2/bootstrap4.html"
    exclude = ("id",)

class SpectraTable(tables.Table):
  created_by = tables.Column(linkify=True)
  lab_name = tables.Column(linkify=True)
  class Meta:
    model = Spectra
    attrs = {"class": "table maintable"}
    template_name = "django_tables2/bootstrap4.html"
    exclude = ("id",)

class MetadataTable(tables.Table):
  class Meta:
    model = Metadata
    attrs = {"class": "table maintable"}
    template_name = "django_tables2/bootstrap4.html"
    exclude = ("id",)

class LabgroupTable(tables.Table):
  class Meta:
    model = LabGroup
    attrs = {"class": "table maintable"}
    template_name = "django_tables2/bootstrap4.html"
    exclude = ("id",)

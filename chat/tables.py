import django_tables2 as tables
from .models import Library

class LibraryTable(tables.Table):
  class Meta:
    model = Library
    template_name = "django_tables2/bootstrap.html"
    exclude = ()

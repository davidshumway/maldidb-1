import django_tables2 as tables
from .models import *
from django.urls import reverse
from django.utils.html import format_html, format_html_join, html_safe

  # ~ owner = models.ForeignKey(
    # ~ settings.AUTH_USER_MODEL,
    # ~ on_delete = models.CASCADE,
    # ~ blank = False,
    # ~ null = False)
  # ~ file = models.FileField(
    # ~ upload_to = 'uploads/',
    # ~ validators=[
      # ~ FileExtensionValidator(allowed_extensions = ['mzml', 'mzxml', 'fid'])
    # ~ ]
  # ~ )
  # ~ upload_date = models.DateTimeField(auto_now_add = True, blank = False)
  # ~ #extension = models.CharField(max_length = 255, blank = True, null = True)
  # ~ spectra = models.ManyToManyField('Spectra', blank = True)
class UserFileTable(tables.Table):
  '''
  '''
  #statuses = tables.ManyToManyColumn(
    # ~ transform = lambda s: s.status,
    # ~ separator = '---***---***---***---'
  #)
  #def render_statuses(self, value):
    # ~ out = []
    # ~ for s in value.all():
      # ~ r = s.status + ' (' + str(s.status_date) + ')'
      # ~ if s.extra != '':
        # ~ s.extra = s.extra[0:40] + '...' if s.extra != None and len(s.extra) > 40 else s.extra
        # ~ n = reverse('chat:user_task_statuses', args=(s.id, ))
        # ~ c = 'info' if s.status == 'info' else 'danger'
        # ~ r += format_html(
          # ~ '<div class="alert alert-{}"><a href="{}">{}</a></div>',
          # ~ c, n, s.extra)
      # ~ out.append(r)
    # ~ return format_html("<br>".join(out))
    
  class Meta:
    model = UserFile
    attrs = {"class": "table maintable"}
    template_name = "chat/bootstrap4_mod.html"
    exclude = ('id', 'owner')
  

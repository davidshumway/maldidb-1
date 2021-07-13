from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import *

class DocsPageAdmin(admin.ModelAdmin):
  # a list of displayed columns name.
  list_display = ['short_title', 'type', 'parent', 'order']
  # ~ get_view_count.admin_order_field = 'parent'
  ordering = ('type', 'parent', 'order')

#admin.site.register(DocsPage, MarkdownxModelAdmin)
admin.site.register(DocsPage, DocsPageAdmin)

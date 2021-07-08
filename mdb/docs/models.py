from django.db import models
from django.template.defaultfilters import slugify
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from django.contrib import admin

class DocsPageAdmin(admin.ModelAdmin):
  list_display = ('short_title', 'order')

class DocsPage(models.Model):
  '''
  ...ordering also applies to sub-categories
  '''
  # ~ slug = models.CharField(max_length = 20) # link / href / id
  short_title = models.CharField(max_length = 200, unique = True, ) # left-hand panel
  long_title = models.CharField(max_length = 200, unique = True, ) # main content title
  type = models.CharField(
    max_length = 20,
    choices = [
      ('category', 'Category'),
      ('sub-category', 'Sub-category'),
      #('top', 'Top'),
    ],
    blank = False,
    null = False
  )
  order = models.IntegerField(blank = False, null = False, default = 1)
  parent = models.ForeignKey( # every sub-category has a parent
    'DocsPage',
    on_delete = models.CASCADE,
    blank = True,
    null = True)
  
  content = MarkdownxField()
  # ~ content = models.TextField(blank = True)
  
  slug = models.SlugField(null = False, unique = True, editable = False)
  
  @admin.display(ordering = 'order')
  
  #class Meta:
  #  ordering = ('order',)

  def formatted_markdown(self):
    '''
    https://github.com/neutronX/django-markdownx/issues/83#issuecomment-500536739
    '''
    return markdownify(self.content)
     
  def __str__(self):
    return self.short_title
    
  def save(self, *args, **kwargs):
    if not self.slug:
      self.slug = slugify(self.long_title)
    return super().save(*args, **kwargs)

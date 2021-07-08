from django.contrib import admin

#from .models import Comment, Spectra
#admin.site.register(Comment)
#admin.site.register(Spectra)

# registers all models
from django.apps import apps
models = apps.get_models()
for model in models:
  # ~ print(f'model{model}')
  # ~ print(f'model vn{model._meta.verbose_name}')
  if model._meta.verbose_name == 'docs page':# loads its own
    continue
  try:
    admin.site.register(model)
  except admin.sites.AlreadyRegistered:
    pass

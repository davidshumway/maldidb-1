from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('chat.urls')),
    path('s/', include('spectra.urls')),
    path('import/', include('importer.urls')),
    path('search/', include('spectra_search.urls')),
    path('files/', include('files.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ~ from django.db.models.loading import cache as model_cache
# ~ if not model_cache.loaded:
    # ~ model_cache.get_models() 
# ~ admin.autodiscover()

"""
URL configuration for leadup project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/learners/dashboard/', permanent=False), name='home'),
    path('accounts/', include('accounts.urls')),
    path('learners/', include('learners.urls')),
    path('admins/', include('admins.urls')),
    path('programs/', include('programs.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

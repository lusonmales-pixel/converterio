"""
URL configuration for File Converter project.
"""

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import serve

from converter import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/detect/', views.detect_format, name='detect_format'),
    path('api/convert/', views.convert_file_view, name='convert'),
    path('', include('accounts.urls')),
    path('', include('plans.urls')),
]

# Serve media in development
if settings.DEBUG:
    from django.urls import re_path
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

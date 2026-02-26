from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('library.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


def error_view(request, exception=None, status=500):
    return render(request, 'error.html', status=status)


handler404 = lambda request, exception: error_view(request, exception, 404)
handler403 = lambda request, exception: error_view(request, exception, 403)
handler500 = lambda request: error_view(request, status=500)

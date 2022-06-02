from django.urls import path, include
from django.conf.urls.static import static

from voicedoc import settings

urlpatterns = [
    path('users',include('users.urls')),
    path('reservations', include('reservations.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

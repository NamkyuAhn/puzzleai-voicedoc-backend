from django.urls import path, include
from django.conf.urls.static import static
from users.views import SigninView

from voicedoc import settings

urlpatterns = [
    path('users',include('users.urls')),
    path('accounts/login', SigninView.as_view())
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

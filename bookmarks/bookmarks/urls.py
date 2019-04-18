from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from account.views import index

urlpatterns = [
    path('', index, name='index'),
    path('account/', include('account.urls')),
    path('admin/', admin.site.urls),
    path('images/', include('images.urls', namespace='images')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

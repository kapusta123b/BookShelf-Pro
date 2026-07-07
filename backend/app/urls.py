from django.contrib import admin
from django.urls import path, include

from django.conf.urls.static import static

from app import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("main.urls")),
    path("books/", include("books.urls")),
    path("library/", include("library.urls")),
    path("users/", include("users.urls")),
    path("accounts/", include("allauth.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include('debug_toolbar.urls'))
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin
from django.urls import path, include

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

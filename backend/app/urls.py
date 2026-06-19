from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("main.urls")),
    path("books/", include("books.urls")),
    path("library/", include("library.urls")),
    path("users/", include("users.urls")),
    path("accounts/", include("allauth.urls")),
]

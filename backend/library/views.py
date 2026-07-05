from django.urls import reverse
from django.views.generic import DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

from django.core.cache import cache

from library.services.changes import change_user_book_status
from library.services.library import LibraryFilters, fetch_library_data

from utils.cache import get_cache_key
from library.services.services import add_book_to_library
from users.models import User


class LibraryView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "public_id"
    slug_url_kwarg = "public_id"
    template_name = "library/index.html"
    context_object_name = "library_user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        filters = self._get_filters()
        cache_key = get_cache_key(f"library:user={self.object.public_id}", filters)

        def fetch_data():
            return fetch_library_data(self.object, filters)

        library_data = cache.get_or_set(cache_key, fetch_data, timeout=600)
        context.update(library_data)
        
        return context

    def _get_filters(self) -> LibraryFilters:
        get = self.request.GET
        return LibraryFilters(
            search=get.get("search"),
            filter_value=get.get("filter", "all"),
            sort=get.get("sort", "recently"),
            page=get.get("page", 1),
            reverse_sort=get.get("reverse_sort") == "true",
        )


class AddToLibraryView(LoginRequiredMixin, View):
    def post(self, request, book_id):
        if book_id:
            add_book_to_library(user=request.user, book_id=book_id)

        referer = request.META.get("HTTP_REFERER")

        if referer:
            return redirect(referer)

        return redirect(reverse("books:index", kwargs={"subject_slug": "all"}))


class ChangeStatus(LoginRequiredMixin, View):
    def post(self, request, book_id):
        status = self.request.POST.get("status")

        if status:
            change_user_book_status(user=request.user, book_id=book_id, status=status)

        referer = request.META.get("HTTP_REFERER")

        if referer:
            return redirect(referer)

        return redirect(reverse("library:index"))

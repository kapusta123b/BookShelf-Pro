from django.urls import reverse

from django.views.generic import DetailView, View

from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import redirect


from utils.helpers import paginate
from utils.search import q_search

from library.services.changes import change_user_book_status
from library.services.library import (
    LibraryCacheFilters,
    LibraryFilters,
    get_library_cache_data,
)
from library.services.services import add_book_to_library

from utils.helpers import get_user_content_timestamp

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

        user_ts = get_user_content_timestamp(self.object)

        data = get_library_cache_data(self.object, user_ts, filters.cache_filters)

        if filters.search:
            books = q_search(
                query=filters.search, queryset=books, search_type="library"
            )

        paginate_books = paginate(data["books"], filters.page, per_page=10)

        context.update(
            {
                "page_obj": paginate_books,
                "reviews": data["reviews"],
                "active_filter": filters.cache_filters.filter_value,
                "count_total": data["counts"]["total"],
                "count_reading": data["counts"]["reading"],
                "count_want_to_read": data["counts"]["want"],
                "count_finished": data["counts"]["read"],
                "reviews_ids": data["reviews_ids"],
            }
        )

        return context

    def _get_filters(self) -> LibraryFilters:
        get = self.request.GET
        return LibraryFilters(
            search=get.get("search"),
            page=get.get("page", 1),
            cache_filters=self._get_cache_filters(),
        )

    def _get_cache_filters(self) -> LibraryCacheFilters:
        get = self.request.GET
        return LibraryCacheFilters(
            filter_value=get.get("filter", "all"),
            sort=get.get("sort", "recently"),
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

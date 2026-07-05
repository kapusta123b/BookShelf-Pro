from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from django.core.cache import cache

from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    DetailView,
    UpdateView,
    View,
)

from django.contrib.auth.mixins import LoginRequiredMixin

from utils.cache import get_cache_key
from books.utils import get_user_book_for_review

from books.forms import CreateReviewForm, UpdateReviewForm

from books.models import Author, Book, Review

from books.services.catalog import (
    CatalogFilters,
    get_catalog_queryset,
    get_matched_authors,
    fetch_more_books,
    get_subject,
)

from books.services.detail import (
    enrich_author_detail,
    enrich_book_detail,
    get_author_books,
)
from books.services.rating import rate_book

from books.selectors import (
    get_review_object,
    get_review_queryset,
    get_reviews,
    get_user_book_context,
)


class CatalogView(ListView):
    template_name = "books/index.html"
    model = Book
    paginate_by = 8
    context_object_name = "books"

    def get(self, request, *args, **kwargs):
        search = request.GET.get("search")
        search_by = request.GET.get("search_by")
        subject = kwargs.get("subject_slug")
        page = request.GET.get("page", 1)

        if search and "research" in request.GET:
            fetch_more_books(search_by, search, page)
            url = reverse("books:index", kwargs={"subject_slug": subject})
            return redirect(f"{url}?search={search}&search_by={search_by}&page={page}")

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        filters = self._get_filters()
        return get_catalog_queryset(filters, self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filters = self._get_filters()
        subject_slug = self.kwargs.get("subject_slug")

        cache_key = get_cache_key("catalog_context", filters)

        def fetch_paginated_data():
            return list(context["object_list"])

        context["object_list"] = cache.get_or_set(
            cache_key, fetch_paginated_data, timeout=300
        )
        context["page_obj"].object_list = context["object_list"]
        context["books"] = context["object_list"]

        context["user_library_ids"] = (
            set(self.request.user.library_books.values_list("book_id", flat=True))
            if self.request.user.is_authenticated
            else set()
        )

        page_obj = context["page_obj"]
        if subject_slug and subject_slug != "all":
            context["queryset_count_current"] = page_obj.paginator.count

        context["queryset_count_total"] = cache.get_or_set(
            "catalog_total_count", lambda: Book.objects.count(), timeout=30
        )

        context["current_subject"] = cache.get_or_set(
            f"subject_{subject_slug}", lambda: get_subject(subject_slug), timeout=600
        )

        authors_cache_key = get_cache_key("catalog_authors", filters)
        context["matched_authors"] = cache.get_or_set(
            authors_cache_key,
            lambda: list(get_matched_authors(filters)),
            timeout=600,
        )

        return context

    def _get_filters(self) -> CatalogFilters:
        get = self.request.GET
        return CatalogFilters(
            search=get.get("search"),
            search_by=get.get("search_by"),
            subject=self.kwargs.get("subject_slug"),
            status=get.get("status"),
            rating=get.get("rating"),
            year_from=get.get("year_from"),
            year_to=get.get("year_to"),
            sort=get.get("sort"),
            page=get.get("page", 1),
            reverse_sort=get.get("reverse_sort") == "true",
        )


class BookDetailView(DetailView):
    model = Book
    template_name = "books/book_detail.html"
    context_object_name = "book"
    slug_url_kwarg = "opl_key"
    slug_field = "openlibrary_key"

    def get_object(self, queryset=None):
        book = super().get_object(queryset)
        
        return enrich_book_detail(book)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.object
        
        context.update(get_user_book_context(self.request.user, book))

        reviews_cache_key = f"book_reviews_{book.openlibrary_key}"
        
        def fetch_cached_reviews():
            return list(get_reviews(book))
            
        context["reviews"] = cache.get_or_set(reviews_cache_key, fetch_cached_reviews, timeout=600)

        return context


class AuthorDetailView(DetailView):
    model = Author
    template_name = "books/author_detail.html"
    context_object_name = "author"
    slug_field = "openlibrary_key"
    slug_url_kwarg = "opl_key"

    def get_object(self, queryset=None):
        opl_key = self.kwargs.get("opl_key")

        author = get_object_or_404(Author, openlibrary_key=opl_key)
        return enrich_author_detail(author)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.POST.get("page") or self.request.GET.get("page", 1)
        opl_key = self.kwargs.get("opl_key")

        author_books_cache_key = f"author_books:{opl_key}_page={page}"

        def fetch_author_books():
            paginator_obj = get_author_books(
                author=self.object, load_from_api=False, page=page
            )

            paginator_obj.object_list = list(paginator_obj.object_list)
            return paginator_obj

        context["page_obj"] = cache.get_or_set(
            author_books_cache_key, fetch_author_books, timeout=300
        )

        context["books"] = context["page_obj"].object_list

        return context

    def post(self, request, *args, **kwargs):
        author = self.get_object()

        page = request.POST.get("page", 1)

        get_author_books(
            author=author,
            load_from_api=True,
            page=page,
        )

        return redirect(request.path + f"?page={page}")


class RateBookView(LoginRequiredMixin, View):
    def post(self, request, book_id):
        try:
            rating = int(request.POST.get("rating", 0))
        except (TypeError, ValueError):
            return redirect(request.META.get("HTTP_REFERER", "/"))

        if not 1 <= rating <= 5:
            return redirect(request.META.get("HTTP_REFERER", "/"))

        rate_book(request.user, book_id, rating)
        return redirect(request.META.get("HTTP_REFERER", "/"))


class CreateReviewView(LoginRequiredMixin, CreateView):
    model = Review
    template_name = "books/create_review.html"
    form_class = CreateReviewForm

    def get_success_url(self):
        opl_key = self.kwargs.get("opl_key")
        return reverse(
            "books:book_detail",
            kwargs={"opl_key": opl_key, "subject_slug": "all"},
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["user"] = self.request.user
        kwargs["opl_key"] = self.kwargs.get("opl_key")

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        opl_key = self.kwargs.get("opl_key")

        context["review_book"] = get_user_book_for_review(
            opl_key=opl_key, user=self.request.user
        )

        return context


class UpdateReviewView(LoginRequiredMixin, UpdateView):
    template_name = "books/update_review.html"
    model = Review
    context_object_name = "review"
    form_class = UpdateReviewForm

    def get_object(self, queryset=None):

        current_queryset = super().get_queryset()

        return get_review_object(
            hash_id=self.kwargs.get("review_hashid"), queryset=current_queryset
        )

    def get_queryset(self):
        return get_review_queryset(self.request.user)

    def get_success_url(self):
        return reverse(
            "books:book_detail",
            kwargs={
                "subject_slug": "all",
                "opl_key": self.object.user_book.book.openlibrary_key,
            },
        )


class DeleteReviewView(LoginRequiredMixin, DeleteView):
    model = Review

    def get_object(self, queryset=None):

        current_queryset = super().get_queryset()

        return get_review_object(
            hash_id=self.kwargs.get("review_hashid"), queryset=current_queryset
        )

    def get_queryset(self):
        return get_review_queryset(self.request.user)

    def get_success_url(self):
        return reverse(
            "books:book_detail",
            kwargs={
                "subject_slug": "all",
                "opl_key": self.object.user_book.book.openlibrary_key,
            },
        )

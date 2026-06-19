from django.shortcuts import redirect
from django.urls import reverse

from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    DetailView,
    UpdateView,
    View,
)

from django.contrib.auth.mixins import LoginRequiredMixin

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
    get_reviews,
    get_user_book_context,
)
from books.services.rating import rate_book


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
        if not hasattr(self, "_cached_queryset"):
            self._cached_queryset = get_catalog_queryset(
                self._get_filters(), self.request.user
            )

        return self._cached_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subject_slug = self.kwargs.get("subject_slug")

        context["user_library_ids"] = (
            set(self.request.user.library_books.values_list("book_id", flat=True))
            if self.request.user.is_authenticated
            else set()
        )
        context["queryset_count_total"] = Book.objects.count()
        context["queryset_count_current"] = self.get_queryset().count()
        context["current_subject"] = get_subject(subject_slug)
        context["matched_authors"] = get_matched_authors(self._get_filters())

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
        )


class BookDetailView(DetailView):
    model = Book
    template_name = "books/book_detail.html"
    context_object_name = "book"
    pk_url_kwarg = "book_id"

    def get_object(self, queryset=None):
        return enrich_book_detail(super().get_object(queryset))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_user_book_context(self.request.user, self.object))
        context.update(get_reviews(self.object))

        return context


class AuthorDetailView(DetailView):
    model = Author
    template_name = "books/author_detail.html"
    context_object_name = "author"
    pk_url_kwarg = "author_id"

    def get_object(self, queryset=None):
        return enrich_author_detail(super().get_object(queryset))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get("page")
        load_author_books = True if "load_more" in self.request.GET else False

        context["author_books"] = get_author_books(
            author=self.get_object(), load_from_api=load_author_books, page=page
        )

        return context


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
        book_id = self.kwargs.get("book_id")
        return reverse(
            "books:book_detail",
            kwargs={"book_id": book_id, "subject_slug": "all"},
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["user"] = self.request.user
        kwargs["book_id"] = self.kwargs.get("book_id")

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        book_id = self.kwargs.get("book_id")

        context["review_book"] = get_user_book_for_review(
            book_id=book_id, user=self.request.user
        )

        return context


class UpdateReviewView(LoginRequiredMixin, UpdateView):
    template_name = "books/update_review.html"
    model = Review
    pk_url_kwarg = "review_id"
    context_object_name = "review"
    form_class = UpdateReviewForm

    def get_queryset(self):
        return self.model.get_review_object(self.request.user)

    def get_success_url(self):
        return reverse(
            "books:book_detail",
            kwargs={
                "subject_slug": "all",
                "book_id": self.object.user_book.book_id,
            },
        )


class DeleteReviewView(LoginRequiredMixin, DeleteView):
    model = Review
    pk_url_kwarg = "review_id"

    def get_queryset(self):
        return self.model.get_review_object(self.request.user)

    def get_success_url(self):
        return reverse(
            "books:book_detail",
            kwargs={
                "subject_slug": "all",
                "book_id": self.object.user_book.book_id,
            },
        )

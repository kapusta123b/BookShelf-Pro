from dataclasses import dataclass

from books.models import Book, BookQuerySet, Subject
from books.services.client import OpenLibaryClient
from books.services.importers import BookImport


@dataclass
class CatalogFilters:
    search: str | None
    search_by: str | None
    subject: str | None
    status: str | None
    rating: str | None
    year_from: str | None
    year_to: str | None
    sort: str | None
    page: str | int


def get_catalog_queryset(filters: CatalogFilters, user=None) -> "BookQuerySet":
    ordering = (
        filters.sort
        if filters.sort and filters.sort != "relevance"
        else "date_created"
    )
    rating_value = (
        int(filters.rating)
        if filters.rating and filters.rating not in ("", "all")
        else None
    )

    queryset = Book.objects

    if filters.search and filters.search_by in ("title", "author", "isbn"):
        queryset = queryset.filter(title__icontains=filters.search)

        if not queryset.exists() or queryset.count() < 8:
            fetch_more_books(filters.search_by, filters.search, filters.page)
            queryset = Book.objects.filter(title__icontains=filters.search)

        return (
            queryset.by_rating(rating_value)
            .by_date(filters.year_from, filters.year_to)
            .order_by(ordering)
        )

    if filters.status and filters.status != "none" and user and user.is_authenticated:
        result = (
            queryset.filter(
                user_entries__user=user, user_entries__status=filters.status
            )
            if filters.status != "all"
            else queryset.filter(user_entries__user=user)
        )
        return (
            result.by_rating(rating_value)
            .by_date(filters.year_from, filters.year_to)
            .order_by(ordering)
        )

    return (
        queryset.by_category(filters.subject)
        .by_date(filters.year_from, filters.year_to)
        .order_by(ordering)
        .by_rating(rating_value)
    )


def fetch_more_books(search_by: str, search: str, page: str | int) -> None:
    docs = OpenLibaryClient().search(argument=search_by, query=search, page=str(page))
    BookImport().save_from_search(docs=docs)


def get_subject(slug: str | None) -> Subject | None:
    if slug and slug != "all":
        return Subject.objects.filter(slug=slug).first()
    return None

from dataclasses import dataclass

from utils.search import q_search
from books.models import Author, Book, BookQuerySet, Subject
from books.services.client import OpenLibaryClient
from books.services.importers import AuthorImport, BookImport


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
    is_relevance_search = bool(filters.search) and filters.search_by == "title" and (
        not filters.sort or filters.sort == "relevance"
    )
    ordering = (
        filters.sort if filters.sort and filters.sort != "relevance" else "date_created"
    )
    rating_value = (
        int(filters.rating)
        if filters.rating and filters.rating not in ("", "all")
        else None
    )

    queryset = Book.objects.prefetch_related("subjects", "authors")

    if filters.search:

        if filters.search_by == "title":
            queryset = search_books(queryset=queryset, filters=filters)

        elif filters.search_by == "author":
            queryset = search_authors(filters=filters)

    if filters.status and filters.status != "none" and user and user.is_authenticated:
        queryset = (
            queryset.filter(
                user_entries__user=user, user_entries__status=filters.status
            )
            if filters.status != "all"
            else queryset.filter(user_entries__user=user)
        )

    qs = (
        queryset.by_category(filters.subject)
        .by_date(filters.year_from, filters.year_to)
        .by_rating(rating_value)
    )

    if not is_relevance_search:
        qs = qs.order_by(ordering)

    return qs


def search_authors(filters):
    authors = Author.objects.filter(name__icontains=filters.search)

    if authors.count() < 8:
        fetch_more_authors(filters.search_by, filters.search, filters.page)
        authors = Author.objects.filter(name__icontains=filters.search)

    return Book.objects.prefetch_related("subjects", "authors").filter(
        authors__in=authors
    )


def search_books(queryset, filters):
    result = q_search(queryset=queryset, query=filters.search, search_type='catalog')

    if result.count() < 8:
        fetch_more_books(filters.search_by, filters.search, filters.page)
        result = q_search(queryset=queryset, query=filters.search, search_type='catalog')

    return result


def fetch_more_books(search_by: str, search: str, page: str | int) -> None:
    docs = OpenLibaryClient().search(argument=search_by, query=search, page=str(page))
    BookImport().save_from_search(docs=docs)


def fetch_more_authors(search_by: str, search: str, page: str | int) -> None:
    docs = OpenLibaryClient().search(argument=search_by, query=search, page=str(page))
    AuthorImport().save_authors_from_search(docs=docs)


def get_matched_authors(filters: CatalogFilters):
    if filters.search and filters.search_by == "author":
        return Author.objects.filter(name__icontains=filters.search)

    return None


def get_subject(slug: str | None) -> Subject | None:
    if slug and slug != "all":
        return Subject.objects.filter(slug=slug).first()

    return None

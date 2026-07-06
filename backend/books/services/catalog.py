from curses.ascii import isdigit
from dataclasses import dataclass

from string import ascii_lowercase

from django.db.models import QuerySet
from django.shortcuts import redirect
from django.urls import reverse

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
    reverse_sort: bool


def get_catalog_queryset(filters: CatalogFilters, user=None) -> "BookQuerySet":
    is_relevance_search = (
        bool(filters.search)
        and filters.search_by == "title"
        and (not filters.sort or filters.sort == "relevance")
    )

    ordering = (
        filters.sort if filters.sort and filters.sort != "relevance" else "date_created"
    )

    rating_value = (
        int(filters.rating)
        if filters.rating and filters.rating not in ("", "all")
        else None
    )

    queryset = Book.objects.all()

    if filters.search:

        if filters.search_by == "title":
            queryset = search_books(filters=filters)

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
        .prefetch_related("subjects", "authors")
    )

    if not is_relevance_search:
        qs = qs.order_by(ordering)

    if filters.reverse_sort:
        qs = qs.reverse()

    return qs


def search_authors(filters: CatalogFilters):
    authors = Author.objects.filter(name__icontains=filters.search)

    if len(authors) < 8:
        fetch_more_authors(filters.search_by, filters.search, filters.page)
        authors = Author.objects.filter(name__icontains=filters.search)

    return Book.objects.prefetch_related("subjects", "authors").filter(
        authors__in=authors
    )


def search_books(filters: CatalogFilters):
    books = Book.objects.filter(title__icontains=filters.search)

    if len(books) < 8:
        fetch_more_books(filters.search_by, filters.search, filters.page)
        books = Book.objects.filter(title__icontains=filters.search)

    return books


def search_by_isbn(filters: CatalogFilters):
    isbn = (
        filters.search.lower().split("isbn")[-1].strip().replace("-", "")
    )  # make ISBN 978-5-389-07435-4 like 9785389074354

    book = Book.objects.filter(isbns__contains=[isbn])

    if not book and isbn.isdigit():
        data = OpenLibaryClient().get_detail(type="isbn", key=isbn)
        BookImport().save_from_isbn(data=data, searched_isbn=isbn)
        book = Book.objects.filter(isbns__contains=[isbn])

    return book


def fetch_more_books(search_by: str, search: str, page: str | int) -> None:
    docs = OpenLibaryClient().search(argument=search_by, query=search, page=str(page))
    BookImport().save_from_search(docs=docs)


def fetch_more_authors(search_by: str, search: str, page: str | int) -> None:
    docs = OpenLibaryClient().search(argument=search_by, query=search, page=str(page))
    AuthorImport().save_authors_from_search(docs=docs)


def get_matched_authors(filters: CatalogFilters) -> QuerySet[Author]:
    if filters.search and filters.search_by == "author":
        return Author.objects.filter(name__icontains=filters.search)

    return Author.objects.none()


def get_subject(slug: str | None) -> Subject | None:
    if slug and slug != "all":
        return Subject.objects.filter(slug=slug).first()

    return None

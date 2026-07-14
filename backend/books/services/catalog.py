from dataclasses import dataclass
import time

from django.urls import reverse

from books.utils import add_subject_page_count, clean_isbn
from books.models import Author, Book
from books.services.client import OpenLibaryClient
from books.services.importers import AuthorImport, BookImport

from django.core.cache import cache


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


def handle_catalog_search(request, filters) -> str | None:

    if not filters.search:
        return None

    if "research" in request.GET or filters.search_by == "subject":
        cache_key = f"{filters.subject}_page_count"

        from books.selectors.catalog import get_subject

        subject_page = cache.get_or_set(
            cache_key,
            lambda: get_subject(filters.subject).openlibrary_page,
            timeout=86400,
        )

        if fetch_and_save_books(filters.search_by, filters.search, subject_page):
            add_subject_page_count(filters.subject)
            cache.delete(cache_key)
            cache.set("books_cache_version", time.time(), timeout=None)

        return reverse("books:index", kwargs={"subject_slug": filters.subject})

    if filters.search_by == "isbn":
        found_book = process_isbn_search(filters.search)
        if found_book:
            return reverse(
                "books:book_detail",
                kwargs={
                    "opl_key": found_book.openlibrary_key,
                    "subject_slug": "all",
                },
            )

    if filters.search_by in ["title", "author"]:
        ensure_search_data_exists(filters)

    return None


def ensure_search_data_exists(filters: CatalogFilters) -> None:

    if filters.search_by == "title":

        if Book.objects.filter(title__icontains=filters.search).count() < 8:
            fetch_and_save_books(filters.search_by, filters.search, filters.page)

    elif filters.search_by == "author":

        if Author.objects.filter(name__icontains=filters.search).count() < 8:
            fetch_and_save_authors(filters.search_by, filters.search, filters.page)


def process_isbn_search(search_string: str) -> Book | None:
    from books.selectors.catalog import get_book_by_isbn

    isbn = clean_isbn(search_string)
    book = get_book_by_isbn(isbn)

    if not book and isbn.isdigit():
        data = OpenLibaryClient().get_detail(type="isbn", key=isbn)

        if data:
            BookImport().save_from_isbn(data=data, searched_isbn=isbn)
            book = get_book_by_isbn(isbn)

    return book


def search_authors(filters: CatalogFilters):
    authors = Author.objects.filter(name__icontains=filters.search)

    if len(authors) < 8:
        fetch_and_save_authors(filters.search_by, filters.search, filters.page)
        authors = Author.objects.filter(name__icontains=filters.search)

    return Book.objects.prefetch_related("subjects", "authors").filter(
        authors__in=authors
    )


def search_books(filters: CatalogFilters):
    books = Book.objects.filter(title__icontains=filters.search)

    if len(books) < 8:
        fetch_and_save_books(filters.search_by, filters.search, filters.page)
        books = Book.objects.filter(title__icontains=filters.search)

    return books


def search_by_isbn(filters: CatalogFilters):
    isbn = clean_isbn(filters.search)  # make ISBN 978-5-389-07435-4 like 9785389074354

    book = Book.objects.filter(isbns__contains=[isbn])

    if not book and isbn.isdigit():
        data = OpenLibaryClient().get_detail(type="isbn", key=isbn)
        BookImport().save_from_isbn(data=data, searched_isbn=isbn)
        book = Book.objects.filter(isbns__contains=[isbn])

    return book


def fetch_and_save_books(search_by: str, search: str, page: str | int) -> None | bool:
    docs = OpenLibaryClient().search(argument=search_by, query=search, page=str(page))
    BookImport().save_from_search(docs=docs)

    return True if docs else False


def fetch_and_save_authors(search_by: str, search: str, page: str | int) -> None:
    docs = OpenLibaryClient().search(argument=search_by, query=search, page=str(page))
    AuthorImport().save_authors_from_search(docs=docs)

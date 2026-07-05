from django.db.models import prefetch_related_objects

from utils.helpers import paginate
from books.models import Author, Book
from books.services.client import OpenLibaryClient
from books.services.importers import AuthorImport, BookImport


def enrich_book_detail(book: Book) -> Book:
    if not book.was_requested_detail:
        raw_doc = OpenLibaryClient().get_detail("works", book.openlibrary_key)
        BookImport().save_from_detail(raw_doc)
        book.refresh_from_db()

    prefetch_related_objects([book], "subjects", "authors")

    return book


def enrich_author_detail(author: Author) -> Author:
    if not author.was_requested_detail:
        raw_doc = OpenLibaryClient().get_detail("authors", author.openlibrary_key)
        AuthorImport().save_from_detail(raw_doc)
        author.refresh_from_db()

    return author


def get_author_books(author: Author, page: str | int, load_from_api=False):
    if load_from_api:
        docs = OpenLibaryClient().search_author_works(
            author_key=author.openlibrary_key,
            page=page,
        )
        BookImport().save_from_search(docs=docs)

    queryset = Book.objects.filter(authors=author).prefetch_related(
        "authors", "subjects"
    )

    return paginate(
        queryset=queryset,
        page_number=page,
        per_page=10,
    )

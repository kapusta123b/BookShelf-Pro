from django.db.models import prefetch_related_objects

from books.models import Author, Book, Review
from books.services.client import OpenLibaryClient
from books.services.importers import AuthorImport, BookImport


def enrich_book_detail(book: Book) -> Book:
    if not book.was_requested_detail:
        raw_doc = OpenLibaryClient().get_detail('works', book.openlibrary_key)
        BookImport().save_from_detail(raw_doc)
        book.refresh_from_db()

    prefetch_related_objects([book], 'subjects', 'authors')

    return book

def enrich_author_detail(author: Author) -> Author:
    if not author.was_requested_detail:
        raw_doc = OpenLibaryClient().get_detail('authors', author.openlibrary_key)
        AuthorImport().save_from_detail(raw_doc)
        author.refresh_from_db()

    return author


def get_user_book_context(user, book: Book) -> dict:
    if not user.is_authenticated:
        return {
            'user_library_ids': set(),
            'user_rating': None,
            'user_rating_pct': 0,
        }

    user_book = user.library_books.filter(book=book).first()
    return {
        'user_library_ids': set(user.library_books.values_list('book_id', flat=True)),
        'user_rating': user_book.rating if user_book else None,
        'user_rating_pct': round(((user_book.rating or 0) / 5) * 100) if user_book else 0,
    }


def get_reviews(book: Book) -> dict:
    reviews = (
    Review.objects
    .filter(user_book__book=book, is_public=True)
    .select_related('user_book')
    )

    return {
        'reviews': reviews
    }
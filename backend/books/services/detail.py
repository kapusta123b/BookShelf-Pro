from books.models import Book
from books.services.client import OpenLibaryClient
from books.services.importers import BookImport


def enrich_book_detail(book: Book) -> Book:
    if not book.was_requested_detail:
        raw_doc = OpenLibaryClient().get_detail(book.openlibrary_key)
        BookImport().save_from_detail(raw_doc)
        book.refresh_from_db()
    
    return book


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

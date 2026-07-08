from books.models import Book
from users.models import User


def get_user_book_context(user: User, book: Book) -> dict:
    if not user.is_authenticated:
        return {
            "user_library_ids": set(),
            "user_rating": None,
            "user_rating_pct": 0,
        }

    user_book = user.library_books.filter(book=book).first()

    return {
        "user_library_ids": set(user.library_books.values_list("book_id", flat=True)),
        "user_rating": user_book.rating if user_book else None,
        "user_rating_pct": (
            round(((user_book.rating or 0) / 5) * 100) if user_book else 0
        ),
    }

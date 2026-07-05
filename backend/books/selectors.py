from django.shortcuts import get_object_or_404

from users.models import User
from books.models import Book, Review

from django.db.models import QuerySet


def get_review_queryset(user: User) -> QuerySet[Review]:
    return (
        Review.objects.filter(user_book__user=user)
        .select_related("user_book")
        .prefetch_related("user_book__book__authors")
    )

def get_review_object(hash_id, queryset=None):

    base_manager = queryset if queryset is not None else Review.objects
    return get_object_or_404(base_manager, hashid=hash_id)

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

def get_reviews(book: Book) -> dict:
    reviews = Review.objects.filter(
        user_book__book=book, is_public=True
    ).select_related("user_book")

    return {"reviews": reviews}
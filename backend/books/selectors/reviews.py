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


def get_reviews(book: Book) -> dict:
    reviews = Review.objects.filter(
        user_book__book=book, is_public=True
    ).select_related("user_book")

    return reviews

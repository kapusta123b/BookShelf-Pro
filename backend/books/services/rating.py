from django.shortcuts import get_object_or_404

from django.db import transaction

from books.services.activity import add_activity
from books.models import Book
from library.models import UserBook


def rate_book(user, book_id: int, rating: int) -> None:
    with transaction.atomic():
        book = get_object_or_404(Book, id=book_id)
        user_book, _ = UserBook.objects.get_or_create(user=user, book=book)

        old_rating = user_book.rating
        user_book.rating = rating
        user_book.save(update_fields=['rating'])

        if old_rating is None:
            book.update_avg_rating(rating)
            action = 'rated'

        else:
            book.update_avg_rating(rating, old_rating=old_rating)
            action = 'change_rate'

        user.update_avg_rating()
        add_activity(user=user, book_id=book_id, rating=rating, action=action)
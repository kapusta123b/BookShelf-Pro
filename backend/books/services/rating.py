from django.shortcuts import get_object_or_404

from django.db import transaction

from users.services import update_user_avg_rating
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
            update_book_avg_rating(book, rating)
            action = 'rated'

        else:
            update_book_avg_rating(book, rating, old_rating=old_rating)
            action = 'change_rate'

        update_user_avg_rating(user)

        add_activity(user=user, book_id=book_id, rating=rating, action=action)

def update_book_avg_rating(book: Book, new_rating: int, old_rating: int | None = None) -> None:
        if old_rating is None:
            book.avg_rating = (book.avg_rating * book.rating_count + new_rating) / (
                book.rating_count + 1
            )
            book.rating_count += 1

        else:
            book.avg_rating = (
                book.avg_rating * book.rating_count - old_rating + new_rating
            ) / book.rating_count

        book.avg_rating = round(book.avg_rating, 2)
        book.save(update_fields=["avg_rating", "rating_count"])
from django.shortcuts import get_object_or_404

from books.models import Book
from library.models import UserBook


def rate_book(user, book_id: int, rating: int) -> None:
    book = get_object_or_404(Book, id=book_id)
    user_book, _ = UserBook.objects.get_or_create(user=user, book=book)

    old_rating = user_book.rating
    user_book.rating = rating
    user_book.save(update_fields=['rating'])

    if old_rating is None:
        book.update_avg_rating(rating)
    else:
        book.update_avg_rating(rating, old_rating=old_rating)

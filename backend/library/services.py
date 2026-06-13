from django.db import transaction

from books.services.activity import add_activity
from library.models import UserBook


def add_book_to_library(book_id, user) -> None:

    with transaction.atomic():
        userbook, created = UserBook.objects.get_or_create(user=user, book_id=book_id)

        if created:
            add_activity(user=user, book_id=book_id, action="added")


def change_user_book_status(book_id: int, user, status: str) -> None:
    with transaction.atomic():
        user_book = (
            UserBook.objects.select_for_update()
            .filter(book_id=book_id, user=user)
            .first()
        )

        if not user_book:
            return None

        created = user_book.change_status(status)

        if created:
            add_activity(user=user, book_id=user_book.book.id, action=status)

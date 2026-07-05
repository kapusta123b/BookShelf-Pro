from django.db import transaction

from django.utils import timezone

from books.services.activity import add_activity

from library.models import UserBook


def add_book_to_library(book_id, user) -> None:

    with transaction.atomic():
        userbook, created = UserBook.objects.get_or_create(user=user, book_id=book_id)

        if created:
            add_activity(user=user, book_id=book_id, action="added")

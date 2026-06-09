from django.db import transaction

from library.models import UserBook
from users.models import RecentActivity

def add_book_to_library(book_id, user) -> None:

    with transaction.atomic():
        userbook, created = UserBook.objects.get_or_create(
            user=user,
            book_id=book_id
        )

        if created:
            RecentActivity.objects.create(
                book_id=book_id,
                user=user,
                action='added'
            )

def change_user_book_status(book_id: int, user, status: str) -> None:
    with transaction.atomic():
        print(book_id)
        user_book = (
        UserBook.objects.select_for_update()
        .filter(id=book_id, user=user)
        .first())

        if not user_book:
            return None
        
        created = user_book.change_status(status)

        if created:
            RecentActivity.objects.create(
                user=user,
                book_id=user_book.book_id,
                action=status
            )

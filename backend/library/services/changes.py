from django.db import transaction

from django.utils import timezone
from utils.helpers import update_user_library_timestamp

from library.models import UserBook

from books.services.activity import add_activity


def change_user_book_status(book_id: int, user, status: str) -> None:

    with transaction.atomic():
        user_book = (
            UserBook.objects.select_for_update()
            .get(book_id=book_id, user=user)
        )

        if not user_book:
            return None

        created = change_status(user_book, status)

        if created:
            add_activity(user=user, book_id=user_book.book.id, action=status)

            update_user_library_timestamp(user)

        return True
    
    return False



def change_status(user_book: UserBook, status: str) -> bool:
    user_book.status = status

    if status == user_book.Status.READING and not user_book.started_at:
        user_book.started_at = timezone.now().date()

    elif status == user_book.Status.READ and not user_book.finished_at:
        user_book.finished_at = timezone.now().date()

    user_book.save(update_fields=["status", "started_at", "finished_at"])

    return True
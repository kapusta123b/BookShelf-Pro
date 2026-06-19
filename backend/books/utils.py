from books.services.subject_map import SUBJECT_MAP

from django.shortcuts import get_object_or_404

from library.models import UserBook


def import_subjects_from_the_map(subject: str) -> str:
    keywords = SUBJECT_MAP.get(subject, [subject])
    parts = [f'subject:"{kw}"' for kw in keywords]
    return " OR ".join(parts)


def get_user_book_for_review(book_id, user):

    queryset = UserBook.objects.select_related("book").prefetch_related("book__authors")

    return get_object_or_404(queryset, book_id=book_id, user=user)

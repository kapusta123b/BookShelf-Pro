from books.services.subject_map import SUBJECT_MAP

from django.shortcuts import get_object_or_404

from library.models import UserBook


def import_subjects_from_the_map(subject: str) -> str:
    keywords = SUBJECT_MAP.get(subject, [subject])
    parts = [f'subject:"{kw}"' for kw in keywords]
    return " OR ".join(parts)


def get_user_book_for_review(opl_key, user):

    queryset = UserBook.objects.select_related("book").prefetch_related("book__authors", 'book__subjects')
    return get_object_or_404(queryset, book__openlibrary_key=opl_key, user=user)


def clean_isbn(search_string: str) -> str:
    return search_string.lower().split("isbn")[-1].strip().replace("-", "")
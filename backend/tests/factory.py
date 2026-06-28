from uuid import uuid4

from books.models import Book
from library.models import UserBook


def create_user_book(user, book, **kwargs):

    defaults = {
        "user": user,
        "book": book,
    }

    defaults.update(kwargs)

    return UserBook.objects.create(**defaults)


def create_book(**kwargs):

    defaults = {
        'title': 'Harry',
        'openlibrary_key': uuid4().hex
    }
    
    defaults.update(kwargs)
    
    return Book.objects.create(**defaults)
from uuid import uuid4

from users.models import User
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


def create_user(username: str = 'User'):
    return User.objects.create_user(username=username)
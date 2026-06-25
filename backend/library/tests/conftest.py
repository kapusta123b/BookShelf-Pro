import pytest

from books.models import Book
from users.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user(username="User")


@pytest.fixture
def book(db):
    return Book.objects.create(title="Title")


@pytest.fixture
def user_book(db, user, book):
    from library.models import UserBook

    return UserBook.objects.create(user=user, book=book)

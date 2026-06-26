
import pytest

from users.models import User
from books.models import Book


@pytest.fixture
def book_queryset(db):
    Book.objects.create(title="Title")

    return Book.objects.all()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="User")

@pytest.fixture
def book(db):
    return Book.objects.create(title="Title")
import pytest

from books.models import Book
from library.models import UserBook
from users.models import User


@pytest.fixture
def user(db):
    user = User.objects.create_user(username="User")

    book1 = Book.objects.create(title="Book 1", openlibrary_key="OL1")

    book2 = Book.objects.create(title="Book 2", openlibrary_key="OL2")

    UserBook.objects.create(user=user, book=book1, rating=4)

    UserBook.objects.create(user=user, book=book2, rating=2)

    return user

import pytest
from unittest.mock import patch

from books.models import Book
from users.models import User
from library.models import UserBook

from backend.library.services.services import (
    add_book_to_library,
    change_status,
    change_user_book_status,
)




def create_book():
    return Book.objects.create(title="Title")

@pytest.mark.django_db
def test_add_book_creates_record(book, user):

    add_book_to_library(book_id=book.id, user=user)

    assert UserBook.objects.filter(user=user, book=book).exists()


@pytest.mark.django_db
@patch("library.services.add_activity")
def test_add_book_creates_activity(mock_activity, book, user):

    add_book_to_library(book_id=book.id, user=user)

    mock_activity.assert_called_once_with(
        user=user,
        book_id=book.id,
        action="added",
    )


@pytest.mark.django_db
@patch("library.services.add_activity")
def test_existing_book_does_not_create_activity(mock_activity, book, user):

    UserBook.objects.create(user=user, book=book)

    add_book_to_library(book_id=book.id, user=user)

    assert UserBook.objects.count() == 1
    mock_activity.assert_not_called()


@pytest.mark.django_db
def test_change_status_sets_finished_at(book, user):

    user_book = UserBook.objects.create(user=user, book=book)

    change_status(user_book, status=UserBook.Status.READ)

    user_book.refresh_from_db()

    assert user_book.status == UserBook.Status.READ
    assert user_book.finished_at is not None


@pytest.mark.django_db
def test_change_status_sets_started_at(book, user):

    user_book = UserBook.objects.create(user=user, book=book)

    change_status(user_book, status=UserBook.Status.READING)

    user_book.refresh_from_db()

    assert user_book.status == UserBook.Status.READING
    assert user_book.started_at is not None


@pytest.mark.django_db
def test_change_user_book_status_updates_existing_record(book, user):

    UserBook.objects.create(user=user, book=book)

    change_user_book_status(
        book_id=book.id,
        user=user,
        status=UserBook.Status.READ,
    )

    user_book = UserBook.objects.get(user=user, book=book)

    assert user_book.status == UserBook.Status.READ
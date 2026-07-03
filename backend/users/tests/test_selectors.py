import pytest

from tests.factory import create_user
from library.models import UserBook
from books.models import Review
from users.selectors import get_profile_data
from tests.factory import create_book, create_user_book


@pytest.mark.django_db
def test_profile_data_groups_books_by_status(user):

    create_user_book(user=user, book=create_book(), status=UserBook.Status.WANT_TO_READ)
    create_user_book(user=user, book=create_book(), status=UserBook.Status.READ)
    create_user_book(user=user, book=create_book(), status=UserBook.Status.READING)

    data = get_profile_data(user)

    assert len(data["reading"]) == 1
    assert len(data["read"]) == 1
    assert len(data["want_to_read"]) == 1


@pytest.mark.django_db
def test_profile_data_contains_user_reviews(user):

    user_book = create_user_book(user=user, book=create_book())

    review = Review.objects.create(
        user_book=user_book,
    )

    data = get_profile_data(user)

    assert review in data["reviews"]
    assert len(data["reviews"]) == 1


@pytest.mark.django_db
def test_profile_data_excludes_other_users_reviews(user):

    other_user = create_user(username="other")

    user_review = Review.objects.create(
        user_book=create_user_book(user=user, book=create_book())
    )

    other_review = Review.objects.create(
        user_book=create_user_book(user=other_user, book=create_book())
    )

    data = get_profile_data(user)

    assert user_review in data["reviews"]
    assert other_review not in data["reviews"]
    assert len(data["reviews"]) == 1


def test_profile_data_limits_reviews_to_five(user):

    for _ in range(7):
        Review.objects.create(
            user_book=create_user_book(
                user=user,
                book=create_book(),
            )
        )

    data = get_profile_data(user)

    assert len(data["reviews"]) == 5

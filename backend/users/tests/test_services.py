import pytest

from tests.factory import create_book, create_user_book
from users.services import update_user_avg_rating


@pytest.mark.django_db
def test_update_user_avg_rating_correctly(user):
    create_user_book(user, create_book(), rating=2)
    create_user_book(user, create_book(), rating=4)

    update_user_avg_rating(user)

    user.refresh_from_db()

    assert user.avg_rating == 3



def test_update_user_avg_without_rating(user):
    update_user_avg_rating(user)

    user.refresh_from_db()

    assert user.avg_rating == 0


def test_update_user_avg_rating_single_rating(user, book):
    create_user_book(user, book, rating=4)

    update_user_avg_rating(user)

    user.refresh_from_db()

    assert user.avg_rating == 4
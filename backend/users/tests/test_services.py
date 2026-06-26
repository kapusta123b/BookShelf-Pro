



import pytest

from users.services import update_user_avg_rating


@pytest.mark.django_db
def test_update_user_avg_rating_correctly(user):

    update_user_avg_rating(user)

    user.refresh_from_db()

    assert user.avg_rating == 3
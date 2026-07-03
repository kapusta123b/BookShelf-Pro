import pytest

from users.models import RecentActivity

@pytest.mark.django_db
def test_get_by_action_returns_correct_icon(user):

    activity = RecentActivity.objects.create(
        user=user, action=RecentActivity.Action.CHANGE_RATE
    )

    assert activity.icon == "change-rate.svg"
    assert activity.icon_class == "change-rate"


def test_unknown_action_returns_default_icon():

    activity = RecentActivity(action="something")

    assert activity.icon == 'plus.svg'
    assert activity.icon_class == 'added'

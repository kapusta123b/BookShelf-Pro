import pytest

from users.models import RecentActivity

from django.core.files.uploadedfile import SimpleUploadedFile

@pytest.mark.django_db
def test_get_by_action_returns_correct_icon(user):

    activity = RecentActivity.objects.create(
        user=user, action=RecentActivity.Action.CHANGE_RATE
    )

    assert activity.icon == "change-rate.svg"
    assert activity.icon_class == "change-rate"


def test_unknown_action_returns_default_icon():

    activity = RecentActivity(action="something")

    assert activity.icon == "plus.svg"
    assert activity.icon_class == "added"


def test_format_avatar_none_initial(user):
    assert user.format_avatar() == ""


def test_format_avatar_returns_correct_initial_with_spaces(user):
    user.first_name = "   Jeoffrey    "
    user.last_name = "   Epstein  "

    assert user.format_avatar() == "J E"


def test_format_avatar_not_contains_first_name(user):
    user.first_name = "Jeoffrey"

    assert user.format_avatar() == "J"


def test_format_avatar_not_contains_last_name(user):
    user.last_name = "Epstein"

    assert user.format_avatar() == "E"

def test_format_avatar_return_user_url_image(user):
    small_gif = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x03'
        b'\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00'
        b'\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
    ) # a 1x1-pixel image in memory
    
    avatar = SimpleUploadedFile(name="avatars/test_avatar.gif", content=small_gif, content_type="image/gif")
    
    user.profile_image = avatar

    assert user.format_avatar() == "/media/test_avatar.gif"



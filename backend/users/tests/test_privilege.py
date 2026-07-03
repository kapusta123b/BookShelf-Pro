from django.urls import reverse
import pytest

@pytest.mark.django_db
def test_anonymous_redirected_from_profile(client, user):

    response = client.get(
        reverse(
            "users:profile",
            kwargs={
                "user_id": user.id,
            },
        )
    )

    assert response.status_code == 302



@pytest.mark.django_db
def test_authenticated_user_can_open_profile(client, user):

    client.force_login(user)

    response = client.get(
        reverse(
            "users:profile",
            kwargs={
                "user_id": user.id,
            },
        )
    )

    assert response.status_code == 200
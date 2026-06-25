


import pytest


@pytest.mark.django_db
def test_user_library_url(client, user):
    url = f'library/{user.id}'

    response = client.get(url)


    assert response.status_code == 200
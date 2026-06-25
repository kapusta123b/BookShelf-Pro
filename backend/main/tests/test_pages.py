from django.test import Client
import pytest

@pytest.mark.django_db
def test_index_page():
    client = Client()

    response = client.get("/")

    assert response.status_code == 200
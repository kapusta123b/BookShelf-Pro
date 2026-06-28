
import pytest

from tests.factory import create_book
from users.models import User

@pytest.fixture
def user(db):
    return User.objects.create_user(username="User")

@pytest.fixture
def book(db):
    return create_book()
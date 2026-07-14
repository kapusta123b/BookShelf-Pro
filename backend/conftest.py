import pytest

from tests.factory import create_book, create_user_book

from users.models import User

from django.utils import timezone



@pytest.fixture
def user(db):
    return User.objects.create_user(username="User1")


@pytest.fixture
def book(db):
    return create_book()


@pytest.fixture
def setup_books(user):
    book_a = create_book(title="A-Book")
    book_b = create_book(title="B-Book")
    
    book_a.authors.create(name="B-Author", openlibrary_key="key_b")
    book_b.authors.create(name="A-Author", openlibrary_key="key_a")

    ub_reading = create_user_book(user, book_a, status="reading")                       
    ub_want = create_user_book(user, book_b, status="want_to_read")
    
    return {
        "user": user,
        "ub_reading": ub_reading,
        "ub_want": ub_want
    }

@pytest.fixture
def ts(user):
    ts = int((user.content_updated_at or timezone.now()).timestamp())
    
    return ts
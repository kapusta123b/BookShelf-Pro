import pytest

from library.selectors import get_library_data

from tests.factory import create_book, create_user_book

from books.models import Review


@pytest.mark.django_db
def test_get_library_data_contains_user_reviews_and_ids(user):

    review = Review.objects.create(
        user_book=create_user_book(user, create_book()),
    )

    data = get_library_data(user)

    assert data["reviews"].filter(user_book__user=user).exists()
    assert review.id in data["reviews_ids"]


@pytest.mark.django_db
def test_get_library_data_contains_user_books_and_correct_count(user):
    book_read = create_user_book(user, create_book(), status='read')
    book_reading = create_user_book(user, create_book(), status='reading')
    book_want = create_user_book(user, create_book()) 

    data = get_library_data(user, status_filter='want_to_read')

    assert book_want in data['books']
    assert book_read and book_reading not in data['books']

    assert data['counts']['want'] == 1
    assert data['counts']['read'] == 1
    assert data['counts']['reading'] == 1


import pytest

from library.models import UserBook
from books.models import Book
from utils.search import q_search

@pytest.mark.django_db
def test_unknown_search_type_returns_none():

    queryset = Book.objects.all()

    result = q_search(
        query='example',
        queryset=queryset,
        search_type='unknown'
    )

    assert result is None


@pytest.mark.django_db
def test_search_returns_matching_book(book, user):

    user_book = UserBook.objects.create(book=book, user=user)


    result = q_search(
        query='Title',
        queryset=UserBook.objects.all(),
        search_type='library'
    )
    
    assert user_book in result


def test_search_not_contains_wrong_book(user, book):

    book1 = Book.objects.create(
        title="Harry Potter",
        openlibrary_key="OL1"
    )

    book2 = Book.objects.create(
        title="Lord of the Rings",
        openlibrary_key="OL2"
    )

    UserBook.objects.create(user=user, book=book1)
    UserBook.objects.create(user=user, book=book2)

    result = q_search(
        query='Harry Potter',
        queryset=UserBook.objects.all(),
        search_type='library'
    )

    assert book2 not in [obj.book for obj in result]
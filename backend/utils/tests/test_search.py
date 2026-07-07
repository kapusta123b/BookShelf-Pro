import pytest

from tests.factory import create_book, create_user_book

from library.models import UserBook

from books.models import Book

from utils.search import q_search


@pytest.mark.django_db
def test_unknown_search_type_returns_none():

    queryset = Book.objects.all()

    result = q_search(query="example", queryset=queryset, search_type="unknown")

    assert result is None


@pytest.mark.django_db
def test_search_returns_matching_book(book, user):

    user_book = create_user_book(user, book)

    result = q_search(
        query="Harry", queryset=UserBook.objects.all(), search_type="library"
    )

    assert result.count() == 1
    assert result.first() == user_book


@pytest.mark.django_db
def test_search_not_contains_wrong_user_book(user):

    book1 = create_book(title="Harry Potter")

    book2 = create_book()

    create_user_book(user, book1)
    create_user_book(user, book2)

    result = q_search(
        query="Harry Potter", queryset=UserBook.objects.all(), search_type="library"
    )

    assert book2 not in [obj.book for obj in result]


@pytest.mark.django_db
def test_search_is_queryset(user, book):

    create_user_book(user, book)

    result = q_search(
        query="Harry", queryset=UserBook.objects.all(), search_type="library"
    )

    assert result.exists()

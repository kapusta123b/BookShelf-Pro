from datetime import date

import pytest

from books.models import Book, Subject
from tests.factory import create_book


@pytest.mark.django_db
def test_by_category_unknown_slug_returns_empty():
    book = create_book()
    book = create_book()

    qs = Book.objects.all()

    filtering = qs.by_category("unknown")

    assert filtering.count() == 0


@pytest.mark.django_db
def test_by_category_valid_slug_filters_books():

    subject_1 = Subject.objects.create(name="Horror", slug="horror")
    subject_2 = Subject.objects.create(name="Romance", slug="romance")

    book = create_book().subjects.add(subject_1)
    book = create_book().subjects.add(subject_2)

    qs = Book.objects.all()

    filtering = qs.by_category("romance")

    assert filtering.first().subjects.first().slug == "romance"


@pytest.mark.django_db
def test_by_rating_valid_value_filters_books():

    book = create_book(avg_rating=5)
    book = create_book(avg_rating=2)

    qs = Book.objects.all()

    result_qs = qs.by_rating(2)

    assert result_qs.first().avg_rating == 2


@pytest.mark.django_db
def test_by_date_range_filters_books_correctly():
    create_book(first_publish_date=date(1000, 1, 1))
    create_book(first_publish_date=date(1005, 5, 12))
    create_book(first_publish_date=date(2026, 7, 14))

    qs = Book.objects.all()

    result_qs = qs.by_date("900", "1100")

    assert result_qs.count() == 2


@pytest.mark.django_db
def test_by_date_range_filters_books_from_year():
    create_book(first_publish_date=date(1000, 1, 1))
    create_book(first_publish_date=date(1005, 5, 12))
    create_book(first_publish_date=date(2026, 7, 14))

    qs = Book.objects.all()

    result_qs = qs.by_date("1100", None)

    assert result_qs.count() == 1


@pytest.mark.django_db
def test_by_date_range_filters_books_to_year():
    create_book(first_publish_date=date(1000, 1, 1))
    create_book(first_publish_date=date(1005, 5, 12))
    create_book(first_publish_date=date(2026, 7, 14))

    qs = Book.objects.all()

    result_qs = qs.by_date(None, "2025")

    assert result_qs.count() == 2
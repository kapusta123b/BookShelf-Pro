import pytest

from library.models import UserBook

def test_user_book_queryset_sorting_by_unknown_value(setup_books):
    qs = UserBook.objects.all()
    
    qs.sort_by('unknown')

    assert qs.ordered is False

@pytest.mark.django_db
def test_user_book_queryset_sorting_by_authors_contains_annotate_field(user, setup_books):
    qs = UserBook.objects.filter(user=user)
    
    result_qs = list(qs.sort_by('authors'))

    assert hasattr(result_qs[0], 'first_author_name')

    assert result_qs[0].book.title == "B-Book"
    assert result_qs[1].book.title == "A-Book"


def test_user_book_queryset_tabs_filter_by_all_returns_all(setup_books):
    qs = UserBook.objects.all()


    assert qs.tabs_filter('all').count() == 2

    reading_qs = qs.tabs_filter("reading")
    assert reading_qs.count() == 1
    assert reading_qs.first() == setup_books["ub_reading"]



@pytest.mark.django_db
def test_user_book_queryset_get_counts(user, setup_books):
    qs = UserBook.objects.filter(user=user)
    
    counts = qs.get_counts()
    
    assert counts["total"] == 2
    assert counts["reading"] == 1
    assert counts["want"] == 1
    assert counts["read"] == 0
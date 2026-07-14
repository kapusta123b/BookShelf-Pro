from django.db.models import QuerySet


from ..models import Book, Author, Subject

from books.services.catalog import CatalogFilters


def get_catalog_queryset(filters: CatalogFilters, user=None) -> QuerySet[Book]:
    is_relevance_search = (
        bool(filters.search)
        and filters.search_by == "title"
        and (not filters.sort or filters.sort == "relevance")
    )

    ordering = (
        filters.sort if filters.sort and filters.sort != "relevance" else "date_created"
    )

    rating_value = (
        int(filters.rating)
        if filters.rating and filters.rating not in ("", "all")
        else None
    )

    queryset = Book.objects.all()

    if filters.search:
        if filters.search_by == "title":
            queryset = queryset.filter(title__icontains=filters.search)
        elif filters.search_by == "author":
            authors = Author.objects.filter(name__icontains=filters.search)
            queryset = queryset.filter(authors__in=authors)

    if filters.status and filters.status != "none" and user and user.is_authenticated:
        if filters.status != "all":
            queryset = queryset.filter(
                user_entries__user=user, user_entries__status=filters.status
            )
        else:
            queryset = queryset.filter(user_entries__user=user)

    qs = (
        queryset.by_category(filters.subject)
        .by_date(filters.year_from, filters.year_to)
        .by_rating(rating_value)
        .prefetch_related("subjects", "authors")
    )

    if not is_relevance_search:
        qs = qs.order_by(ordering)

    if filters.reverse_sort:
        qs = qs.reverse()

    return qs


def get_matched_authors(filters: CatalogFilters) -> QuerySet[Author]:
    if filters.search and filters.search_by == "author":
        return Author.objects.filter(name__icontains=filters.search)

    return Author.objects.none()


def get_subject(slug: str | None) -> Subject | None:
    if slug and slug != "all":
        return Subject.objects.filter(slug=slug).first()

    return None


def get_book_by_isbn(isbn: str) -> Book | None:
    return Book.objects.filter(isbns__contains=[isbn]).first()

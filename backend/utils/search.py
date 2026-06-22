from django.db.models import QuerySet
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

_map = {
    "library": (
        "book__title",
        "book__authors__name",
        "book__first_publish_date",
        "book_id",
        "openlibrary_key",
    ),

    "catalog": (
        "title",
    ),
}


def q_search(query: str, queryset: QuerySet, search_type: str) -> QuerySet | None:

    if search_type not in _map:
        return None

    vector = SearchVector(*_map[search_type])

    search_query = SearchQuery(query)

    result = (
        queryset.annotate(rank=SearchRank(vector, search_query))
        .filter(rank__gte=0.01)
        .distinct()
        .order_by("-rank")
    )

    return result.none()

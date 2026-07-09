from dataclasses import dataclass

from library.selectors import get_library_data
from users.models import User


@dataclass
class LibraryCacheFilters:
    filter_value: str
    sort: str
    reverse_sort: bool


@dataclass
class LibraryFilters:
    search: str
    page: str | int
    cache_filters: LibraryCacheFilters


def fetch_library_cache_data(user: User, cache_filters: LibraryCacheFilters) -> dict:
    library_data = get_library_data(
        user, cache_filters.filter_value, cache_filters.sort, cache_filters.reverse_sort
    )

    return {
        "books": list(library_data["books"]),
        "reviews": list(library_data["reviews"]),
        "counts": library_data["counts"],
        "reviews_ids": library_data["reviews_ids"],
    }
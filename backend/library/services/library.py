from dataclasses import dataclass

from library.selectors import get_library_data
from users.models import User

from django.core.cache import cache

from utils.cache import get_cache_key


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


def get_library_cache_data(user: User, ts: float, cache_filters: LibraryCacheFilters) -> dict:

    cache_key = get_cache_key(f"library:user={user.public_id}:ts{ts}", cache_filters)

    def fetch_library_data():
        return get_library_data(
            user,
            cache_filters.filter_value,
            cache_filters.sort,
            cache_filters.reverse_sort,
        )

    cached_data = cache.get_or_set(
        cache_key,
        fetch_library_data,
        timeout=86400,
    )

    return {
        "books": list(cached_data["books"]),
        "reviews": list(cached_data["reviews"]),
        "counts": cached_data["counts"],
        "reviews_ids": cached_data["reviews_ids"],
    }

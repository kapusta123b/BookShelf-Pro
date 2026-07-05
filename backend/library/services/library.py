from dataclasses import dataclass

from library.selectors import get_library_data
from utils.helpers import paginate
from utils.search import q_search
from users.models import User


@dataclass
class LibraryFilters:
    search: str
    filter_value: str
    page: str | int
    sort: str
    reverse_sort: bool


def fetch_library_data(user: User, filters: LibraryFilters) -> dict:
    library_data = get_library_data(user, filters.filter_value, filters.sort, filters.reverse_sort)

    if filters.search:
        library_data["books"] = q_search(query=filters.search, queryset=library_data["books"], search_type="library")

    books_list = list(library_data["books"])

    paginate_books = paginate(books_list, filters.page, per_page=10)

    reviews_list = list(library_data["reviews"])

    return {
        "page_obj": paginate_books,
        "reviews": reviews_list,
        "active_filter": filters.filter_value,
        "count_total": library_data["counts"]["total"],
        "count_reading": library_data["counts"]["reading"],
        "count_want_to_read": library_data["counts"]["want"],
        "count_finished": library_data["counts"]["read"],
        "reviews_ids": library_data["reviews_ids"],
    }

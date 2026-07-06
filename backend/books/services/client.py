import logging

from httpx import Client
from requests import status_codes

from books.utils import import_subjects_from_the_map

logger = logging.getLogger(__name__)

SEARCH_FIELDS = "key,cover_i,title,author_name,author_key,first_publish_year,subject"

_http_client = Client(
    base_url="https://openlibrary.org",
    headers={
        "User-Agent": "BookShelf Pro/1.0, https://github.com/kapusta123b/BookShelf-Pro"
    },
    timeout=25,
    http2=True,
    follow_redirects=True,
)


class OpenLibaryClient:

    def _get(self, path: str, params: dict | None) -> tuple[dict | None, int | None]:
        status_code = None

        try:
            response = _http_client.get(path, params=params)
            status_code = response.status_code
            response.raise_for_status()

            return response.json(), status_code

        except Exception:
            logger.exception("OpenLibrary request failed: %s", path)
            return None, status_code

    def search(
        self, argument: str, query: str, page: str | None, limit: int = 10
    ) -> list[dict] | None:

        if argument == "subject":
            query = import_subjects_from_the_map(subject=query)
            argument = "q"

        data, status_code = self._get(
            path="/search.json",
            params={
                argument: query,
                "fields": SEARCH_FIELDS,
                "page": page,
                "limit": limit,
            },
        )

        return data.get("docs", []) if data and status_code == 200 else None

    def get_detail(self, type: str, key: str) -> dict | None:
        data, status_code = self._get(path=f"/{type}/{key}.json", params=None)
        return data if status_code == 200 else None
        

    def search_author_works(
        self, author_key: str, page: str | int | None = 1, limit: int = 30
    ) -> list[dict] | None:
        return self.search(
            argument="author_key",
            query=author_key,
            page=str(page or 1),
            limit=limit,
        )

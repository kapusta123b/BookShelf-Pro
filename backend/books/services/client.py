import requests

from books.utils import import_subjects_from_the_map
from books.services.importers import SubjectImporter

SEARCH_FIELDS = 'key,cover_i,title,author_name,author_key,first_publish_year,subject'

class OpenLibaryClient:
    BASE_URL = "https://openlibrary.org"
    HEADERS = {"User-Agent": "BookShelf Pro/1.0, https://github.com/kapusta123b/BookShelf-Pro"}
    TIMEOUT = 10

    def _get(self, path: str, params: dict | None) -> dict | None:
        try:
            response = requests.get(
                url=f"{self.BASE_URL}{path}", params=params, timeout=self.TIMEOUT
            )
            response.raise_for_status()
            
            return response.json()
        
        except Exception:
            return None

    def search(self, argument: str, query: str, page: str | None, limit: int = 10) -> list[dict] | None:
        
        if argument == 'subject':
            query = import_subjects_from_the_map(subject=query)
            argument = 'q'

        data = self._get(
            path="/search.json",
            params={
                argument: query,
                "fields": SEARCH_FIELDS,
                "page": page,
                "limit": limit,
            },
        )

        return data.get("docs", []) if data else None

    def get_detail(self, book_key: str) -> dict | None:
        return self._get(
            path=f'/books/{book_key}.json',
            params=None
        )

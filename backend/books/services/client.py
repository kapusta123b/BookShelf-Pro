import requests

from books.services.importers import SubjectImporter

SEARCH_FIELDS = 'key,cover_i,title,author_name,author_key,first_publish_year,subject'

class OpenLibaryClient:
    BASE_URL = "https://openlibrary.org"
    HEADERS = {"User-Agent": "BookShelf Pro/1.0"}
    TIMEOUT = 10

    def _get(self, path: str, params: dict | None) -> dict:

        response = requests.get(
            url=f"{self.BASE_URL}{path}", params=params, timeout=self.TIMEOUT
        )

        response.raise_for_status()
        return response.json()


    def search(self, argument: str, query: str, page: str | None, limit=10) -> dict:
        if argument == 'subject':
            query = SubjectImporter().import_subjects_from_the_map(subject=query)
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

        return data.get("docs", [])
    
    def get_detail(self, book_key: str) -> dict:
        return self._get(
            path=f'/books/{book_key}.json',
        )




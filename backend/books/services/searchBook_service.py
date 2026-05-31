import requests


class BookSearchClient:
    BASE_URL = 'https://openlibrary.org/'

    def search_books_by_argument(self, query: str, argument: str, page: str | None) -> dict:

        url = f'{self.BASE_URL}search.json/'

        response = requests.get(
            url=url,                    
            params={
                argument: query,
                'fields': 'cover_i,title,author_name,author_key,first_publish_year,subject',
                'page': page,
                'limit': 12
            }
        )

        response.raise_for_status()
        data = response.json()

        return data.get('docs', [])
    
    def import_subjects_in_map(self,  subject) -> str:
        pass

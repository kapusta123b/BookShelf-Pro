import requests

from books.services.subject_map import SUBJECT_MAP


class BookSearchClient:
    BASE_URL = 'https://openlibrary.org/'

    def search_books_by_argument(self, query: str, argument: str, page: str | None) -> dict:

        url = f'{self.BASE_URL}search.json/'

        if argument == 'subject':
            query = self.import_subjects_from_the_map(subject=query)
            argument = 'q'

        response = requests.get(
            url=url,                    
            params={
                argument: query,
                'fields': 'cover_i,title,author_name,author_key,first_publish_year,subject',
                'page': page,
                'limit': 10
            },
            timeout=10
        )

        response.raise_for_status()
        data = response.json()

        return data.get('docs', [])
    
    def import_subjects_from_the_map(self, subject: str) -> str:
        keywords = SUBJECT_MAP.get(subject, [subject])

        parts = [f'subject:"{kw}"' for kw in keywords]
        return ' OR '.join(parts)

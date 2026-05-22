

from books.models import Book


class BookImportService:

    def save_and_return_books(self, json: dict):
        if json:
            for data in json:
                
                pass
    
    def clean_data(self, docs: list) -> list:
        clean = []

        for data in docs:
            if data.get('cover_i') and data.get('subject'):
                clean.append(data)

        return clean
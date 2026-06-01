from books.services.subject_map import SUBJECT_MAP
from books.models import Author, Book, Subject
from django.utils.text import slugify


class BookImportService:

    def create_books(self, json: dict) -> None | Book:
        if json:
            clean_data = self.clean_data(json)

            result = []

            for data in clean_data:
                book, _ = Book.objects.update_or_create(
                    cover_i=data["cover_i"],
                    title=data["title"],
                    first_publish_year=data.get("first_publish_year"),
                )

                authors = self.create_authors(
                    names=data["author_name"], keys=data["author_key"]
                )
                subjects = self.get_or_create_subjects(data["subject"])

                book.authors.add(*authors)
                book.subjects.add(*subjects)

                result.append(book)

            return result

        else:
            return None

    def create_authors(self, names: list, keys: list):
        result = []
        for i, name in enumerate(names):
            author, _ = Author.objects.update_or_create(
                openlibrary_key=keys[i], defaults={"name": name}
            )
            result.append(author)

        return result

    def get_or_create_subjects(self, raw_subjects: list):
        genre_names = self.resolve_subjects(raw_subjects)

        result = []
        for name in genre_names:
            subject, _ = Subject.objects.get_or_create(
                slug=slugify(name), defaults={"name": name}
            )

            result.append(subject)

        return result

    def resolve_subjects(self, raw_subjects: list):
        result = set()

        for raw in raw_subjects:
            raw = raw.lower().strip()

            for genre, keywords in SUBJECT_MAP.items():
                if raw in keywords:
                    result.add(genre)
                    break
        return list(result)

    def clean_data(self, docs: dict) -> list:
        clean = []

        for data in docs:
            if data.get("cover_i") and data.get("subject") and data.get("author_key"):
                clean.append(data)

        return clean

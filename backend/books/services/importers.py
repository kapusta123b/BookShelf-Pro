from datetime import date, datetime

from books.services.subject_map import SUBJECT_MAP

from books.models import Author, Book, Subject

from django.utils.text import slugify


class BookImport:

    def save_from_search(self, docs: list[dict] | None) -> list[Book] | None:
        return [self._upsert_book(doc) for doc in docs if self._is_valid(doc)] if docs else None

    def save_from_detail(self, data: dict | None) -> None:
        if not data:
            return

        excerpts = data.get('excerpts', [])
        excerpt_text = excerpts[0].get('excerpt') if excerpts else None

        raw_description = data.get('description')
        if isinstance(raw_description, dict):
            description = raw_description.get('value', '')
        else:
            description = raw_description or ''

        clean_date = self._format_data(data.get('first_publish_date', ''))

        defaults: dict = {
            'cover_ids': [cover for cover in data.get('covers', []) if cover > 0],
            'description': description,
            'excerpt': excerpt_text,
            'was_requested_detail': True,
        }

        if clean_date:
            defaults['first_publish_date'] = clean_date

        Book.objects.update_or_create(
            openlibrary_key=self._clear_key(data['key']),
            defaults=defaults,
        )

    def _upsert_book(self, data: dict) -> Book:
        book, _ = Book.objects.update_or_create(
            openlibrary_key=self._clear_key(data['key']),
            defaults={
                'title': data['title'],
                'cover_i': data.get('cover_i'),
                'first_publish_date': self._format_data(data.get('first_publish_year')),
            }
        )

        subjects = SubjectImporter().save_many(data['subject'])
        authors = AuthorImporter().save_many(
            names=data["author_name"], keys=data["author_key"]
        )
        book.authors.add(*authors)
        book.subjects.add(*subjects)

        return book

    @staticmethod
    def _is_valid(data: dict) -> bool:
        return bool(
            data.get("cover_i")
            and data.get("subject")
            and data.get("author_key")
            and data.get("author_name")
            and data.get("key")
        )

    @staticmethod
    def _format_data(raw_date: str | int | None) -> date | None:
        if not raw_date:
            return None

        raw_date = str(raw_date).strip()

        if raw_date.isdigit():
            return datetime.strptime(raw_date, "%Y").date()

        try:
            return datetime.strptime(raw_date, "%B %d, %Y").date()
        except ValueError:
            try:
                return datetime.strptime(raw_date, "%B, %Y").date()
            except ValueError:
                return None

    @staticmethod
    def _clear_key(raw_key: str) -> str:
        return raw_key.split('/')[-1]


class AuthorImporter:

    def save_many(self, names: list[str], keys: list[str]) -> list[Author]:
        result = []
        
        for key, name in zip(keys, names):
            author, _ = Author.objects.update_or_create(
                openlibrary_key=key,
                defaults={'name': name}
            )
            result.append(author)

        return result


class SubjectImporter:

    def save_many(self, raw_subjects: list[str]) -> list[Subject]:
        result = []

        for name in self._resolve(raw_subjects):
            subject, _ = Subject.objects.get_or_create(
                slug=slugify(name), defaults={"name": name}
            )
            result.append(subject)

        return result

    @staticmethod
    def _resolve(raw_subjects: list[str]) -> list[str]:
        result = set()

        for raw in raw_subjects:
            raw = raw.lower().strip()
            
            for genre, keywords in SUBJECT_MAP.items():
                if raw in keywords:
                    result.add(genre)
                    break

        return list(result)

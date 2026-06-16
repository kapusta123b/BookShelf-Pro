from curses.ascii import isdigit
from datetime import date, datetime

from httpx import get

from books.services.subject_map import SUBJECT_MAP

from books.models import Author, Book, Subject

from django.utils.text import slugify


class BookImport:

    def save_from_search(self, docs: list[dict] | None) -> list[Book] | None:
        return [self._upsert_book(doc) for doc in docs if self._is_valid(doc)] if docs else None
    
    def _upsert_book(self, data: dict) -> Book:
        book, _ = Book.objects.update_or_create(
            openlibrary_key=_clear_key(data['key']),
            defaults={
                'title': data['title'],
                'cover_i': data.get('cover_i'),
                'first_publish_date': _format_data(data.get('first_publish_year')),
            }
        )

        subjects = SubjectImport().save_many(data['subject'])
        authors = AuthorImport().save_many(
            names=data["author_name"], keys=data["author_key"]
        )
        book.authors.add(*authors)
        book.subjects.add(*subjects)

        return book

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

        clean_date = _format_data(data.get('first_publish_date', ''))

        defaults: dict = {
            'cover_ids': _clean_covers(data.get('covers', [])),
            'description': description,
            'excerpt': excerpt_text,
            'was_requested_detail': True,
        }

        if clean_date:
            defaults['first_publish_date'] = clean_date

        Book.objects.update_or_create(
            openlibrary_key=_clear_key(data['key']),
            defaults=defaults,
        )

    @staticmethod
    def _is_valid(data: dict) -> bool:
        return bool(
            data.get("cover_i")
            and data.get("subject")
            and data.get("author_key")
            and data.get("author_name")
            and data.get("key")
        )

class AuthorImport:

    def save_from_detail(self, data: dict | None) -> None:
        if not data:
            return
        
        death_date = data.get('death_date')
        full_name = data.get('full_name')
        raw_bio = data.get('bio')

        raw_bio = raw_bio.get('value', '') if isinstance(raw_bio, dict) else raw_bio
        
        defaults: dict = {
            'biography': raw_bio,
            'birth_date': _format_data(data.get('birth_date')),
            'cover_ids': _clean_covers(data.get('photos', [])),
            'was_requested_detail': True,
            'known_as': data.get('alternate_names', [])
        }

        if death_date:
            defaults['death_date'] = _format_data(death_date)

        if full_name:
            defaults['full_name'] = full_name

        Author.objects.update_or_create(
            openlibrary_key=_clear_key(data['key']),
            defaults=defaults
        )
        

    def save_many(self, names: list[str], keys: list[str]) -> list[Author]:
        result = []
        
        for key, name in zip(keys, names):
            author, _ = Author.objects.update_or_create(
                openlibrary_key=key,
                defaults={'name': name}
            )
            result.append(author)

        return result


class SubjectImport:

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
                try:
                    return datetime.strptime(raw_date, "%d %B %Y").date()

                except ValueError:
                    return None
            

def _clear_key(raw_key: str) -> str:
        return raw_key.split('/')[-1]

def _clean_covers(covers: list) -> list:
    return [cover for cover in covers if covers and isinstance(cover, int) and cover > 0]

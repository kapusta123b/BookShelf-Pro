from books.services.subject_map import SUBJECT_MAP

from books.models import Author, Book, Subject

from django.utils.text import slugify


class BookImport:

    def save_from_search(self, docs: dict[list]) -> list[Book]:
        return [self._upsert_book(doc) for doc in docs if self._is_valid(doc)]

    def save_from_detail(self, data: dict):
        covers = [cover for cover in data['covers'] if cover > 0]

        book, _ = Book.objects.update_or_create(
            openlibrary_key=self._clear_key(data['key']),
            defaults={
                'cover_ids': [
                    cover for cover in data.get('covers', [])
                    if cover > 0],
                'description': data['description']
            }
        )

    def _upsert_book(self, data: dict):
        book, _ = Book.objects.update_or_create(
            openlibrary_key=self._clear_key(data['key']),
            defaults={
                'title': data['title'],
                'cover_i': data['cover_i'],
                'first_publish_year': data.get('first_publish_year'),
            }
        )

        subjects = SubjectImporter().save_many(data['subject'])
        authors = AuthorImporter().save_many(
            names=data["author_name"], keys=data["author_key"]
        )
        book.authors.add(*authors)
        book.subjects.add(*subjects)


    def _is_valid(self, data: dict):
        return bool(
            data.get("cover_i")
            and data.get("subject")
            and data.get("author_key")
            and data.get("author_name")
            and data.get("key")
        )
    
    def _clear_key(self, raw_key: str) -> str:
        return raw_key.strip('works/books')
    


class AuthorImporter:

    def save_many(self, names: list, keys: list) -> list[Author]:
        result = []
        for key, name in zip(keys, names):
            author, _ = Author.objects.update_or_create(
                openlibrary_key=key,
                defaults={
                    'name': name
                }
            )
            result.append(author)
        return result



class SubjectImporter:

    def save_many(self, raw_subjects: list) -> list[Subject]:
        result = []
        for name in self._resolve(raw_subjects):
            subject, _ = Subject.objects.get_or_create(
                slug=slugify(name), defaults={"name": name}
            )
            result.append(subject)
        
        return result
    
    def import_subjects_from_the_map(self, subject: str) -> str:
        keywords = SUBJECT_MAP.get(subject, [subject])

        parts = [f'subject:"{kw}"' for kw in keywords]
        return ' OR '.join(parts)

    @staticmethod
    def _resolve(raw_subjects: list) -> list[str]:
        result = set()
        for raw in raw_subjects:
            raw = raw.lower().strip()

            for genre, keywords in SUBJECT_MAP.items():
                if raw in keywords:

                    result.add(genre)
                    break

        return list(result)
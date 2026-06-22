from __future__ import annotations

from datetime import datetime, date
from typing import Iterable

from django.db import transaction
from django.utils.text import slugify

from books.models import Author, Book, Subject
from books.services.subject_map import SUBJECT_MAP


def _format_data(raw_date: str | int | None) -> date | None:
    if not raw_date:
        return None

    raw_date = str(raw_date).strip()

    if raw_date.isdigit():
        return datetime.strptime(raw_date, "%Y").date()

    for fmt in ("%B %d, %Y", "%B, %Y", "%d %B %Y"):
        try:
            return datetime.strptime(raw_date, fmt).date()
        except ValueError:
            pass

    return None


def _clear_key(raw_key: str) -> str:
    return raw_key.split("/")[-1]


def _clean_covers(covers: list) -> list[int]:
    return [cover for cover in covers if isinstance(cover, int) and cover > 0]


class SubjectImport:
    def bulk_upsert(self, raw_subjects: list[str] | None) -> list[Subject]:
        if not raw_subjects:
            return []

        names = self._resolve(raw_subjects)
        if not names:
            return []

        slugs = [slugify(name) for name in names]
        existing = Subject.objects.in_bulk(slugs, field_name="slug")

        to_create = [
            Subject(slug=slugify(name), name=name)
            for name in names
            if slugify(name) not in existing
        ]

        if to_create:
            Subject.objects.bulk_create(to_create, batch_size=1000, ignore_conflicts=True)

        return list(Subject.objects.filter(slug__in=slugs))

    @staticmethod
    def _resolve(raw_subjects: list[str]) -> list[str]:
        result = set()

        for raw in raw_subjects:
            normalized = raw.lower().strip()

            for genre, keywords in SUBJECT_MAP.items():
                if normalized in keywords:
                    result.add(genre)
                    break

        return list(result)


class AuthorImport:
    @transaction.atomic
    def save_authors_from_search(self, docs: list[dict] | None) -> list[Author] | None:
        if not docs:
            return None

        valid_docs = [doc for doc in docs if self._is_valid_author(doc)]
        
        if not valid_docs:
            return []

        payload = [
            Author(
                openlibrary_key=_clear_key(doc["key"]),
                name=doc["name"],
                birth_date=_format_data(doc.get("birth_date")),
            )
            for doc in valid_docs
        ]

        self._bulk_upsert_authors(payload)

        keys = [_clear_key(doc["key"]) for doc in valid_docs]
        return list(Author.objects.filter(openlibrary_key__in=keys))

    @transaction.atomic
    def save_from_works(self, entries: list[dict] | None) -> list[Book] | None:
        if not entries:
            return None

        valid_entries = [doc for doc in entries if self._is_valid_author_work(doc)]
        if not valid_entries:
            return []

        books = []
        all_subjects: set[str] = set()
        all_author_keys: set[str] = set()

        for doc in valid_entries:
            defaults = BookImport.get_detail_information(doc)

            if defaults["cover_ids"]:
                defaults["cover_i"] = defaults["cover_ids"][0]

            book_key = _clear_key(doc["key"])
            books.append(
                Book(
                    openlibrary_key=book_key,
                    title=defaults["title"],
                    cover_i=defaults.get("cover_i"),
                    cover_ids=defaults["cover_ids"],
                    description=defaults["description"],
                    excerpt=defaults["excerpt"],
                    was_requested_detail=defaults["was_requested_detail"],
                    first_publish_date=defaults.get("first_publish_date"),
                )
            )

            all_subjects.update(doc.get("subjects", []))

            for item in doc.get("authors", []):
                author_data = item.get("author")
                if author_data and author_data.get("key"):
                    all_author_keys.add(_clear_key(author_data["key"]))

        SubjectImport().bulk_upsert(list(all_subjects))
        self._bulk_upsert_author_keys(list(all_author_keys))
        Book.objects.bulk_create(
            books,
            batch_size=1000,
            update_conflicts=True,
            update_fields=[
                "title",
                "cover_i",
                "cover_ids",
                "description",
                "excerpt",
                "was_requested_detail",
                "first_publish_date",
            ],
            unique_fields=["openlibrary_key"],
        )

        saved_books = {
            book.openlibrary_key: book
            for book in Book.objects.filter(
                openlibrary_key__in=[_clear_key(doc["key"]) for doc in valid_entries]
            )
        }

        saved_authors = {
            author.openlibrary_key: author
            for author in Author.objects.filter(openlibrary_key__in=list(all_author_keys))
        }

        saved_subjects = {
            subject.slug: subject
            for subject in Subject.objects.filter(
                slug__in=[slugify(name) for name in SubjectImport()._resolve(list(all_subjects))]
            )
        }

        self._bulk_create_book_relations_from_works(
            valid_entries,
            saved_books=saved_books,
            saved_authors=saved_authors,
            saved_subjects=saved_subjects,
        )

        return list(saved_books.values())

    @transaction.atomic
    def save_from_detail(self, data: dict | None) -> None:
        if not data:
            return

        death_date = data.get("death_date")
        full_name = data.get("full_name")
        raw_bio = data.get("bio")
        raw_bio = raw_bio.get("value", "") if isinstance(raw_bio, dict) else raw_bio

        defaults = {
            "biography": raw_bio or "",
            "birth_date": _format_data(data.get("birth_date")),
            "cover_ids": _clean_covers(data.get("photos", [])),
            "was_requested_detail": True,
            "known_as": data.get("alternate_names", []),
            "name": data.get("name"),
        }

        if death_date:
            defaults["death_date"] = _format_data(death_date)

        if full_name:
            defaults["full_name"] = full_name

        Author.objects.update_or_create(
            openlibrary_key=_clear_key(data["key"]),
            defaults=defaults,
        )

    def _bulk_upsert_authors(self, authors: list[Author]) -> None:
        if not authors:
            return

        Author.objects.bulk_create(
            authors,
            batch_size=1000,
            update_conflicts=True,
            update_fields=["name", "birth_date"],
            unique_fields=["openlibrary_key"],
        )

    def _bulk_upsert_author_keys(self, keys: list[str]) -> None:
        if not keys:
            return

        unique_keys = list(dict.fromkeys(keys))
        existing = Author.objects.in_bulk(unique_keys, field_name="openlibrary_key")

        to_create = [
            Author(openlibrary_key=key, name="")
            for key in unique_keys
            if key not in existing
        ]

        if to_create:
            Author.objects.bulk_create(
                to_create,
                batch_size=1000,
                ignore_conflicts=True,
            )

    def _bulk_create_book_relations_from_works(
        self,
        entries: list[dict],
        saved_books: dict[str, Book],
        saved_authors: dict[str, Author],
        saved_subjects: dict[str, Subject],
    ) -> None:
        book_author_through = Book.authors.through
        book_subject_through = Book.subjects.through

        book_author_links = []
        book_subject_links = []

        for doc in entries:
            book_key = _clear_key(doc["key"])
            book = saved_books.get(book_key)
            if not book:
                continue

            subjects = SubjectImport()._resolve(doc.get("subjects", []))
            for subject_name in subjects:
                subject = saved_subjects.get(slugify(subject_name))
                if subject:
                    book_subject_links.append(
                        book_subject_through(book_id=book.id, subject_id=subject.id)
                    )

            for item in doc.get("authors", []):
                author_data = item.get("author")
                if not author_data or not author_data.get("key"):
                    continue

                author_key = _clear_key(author_data["key"])
                author = saved_authors.get(author_key)
                if author:
                    book_author_links.append(
                        book_author_through(book_id=book.id, author_id=author.id)
                    )

        if book_author_links:
            book_author_through.objects.bulk_create(
                book_author_links, batch_size=1000, ignore_conflicts=True
            )

        if book_subject_links:
            book_subject_through.objects.bulk_create(
                book_subject_links, batch_size=1000, ignore_conflicts=True
            )

    @staticmethod
    def _is_valid_author(data: dict) -> bool:
        required_keys = ["birth_date", "key", "name"]
        return all(data.get(key) for key in required_keys)

    @staticmethod
    def _is_valid_author_work(data: dict) -> bool:
        required_keys = ["title", "key", "authors", "subjects"]
        return all(data.get(key) for key in required_keys)


class BookImport:

    @transaction.atomic
    def save_from_search(self, docs: list[dict] | None) -> list[Book] | None:
        if not docs:
            return None

        valid_docs = [doc for doc in docs if self._is_valid(doc)]

        if not valid_docs:

            return []

        author_payload: list[Author] = []
        all_subjects: set[str] = set()

        for doc in valid_docs:

            for key, name in zip(doc["author_key"], doc["author_name"]):
                author_payload.append(
                    Author(openlibrary_key=_clear_key(key), name=name)
                )

            all_subjects.update(doc.get("subject", []))

        AuthorImport()._bulk_upsert_authors(author_payload)
        subjects = SubjectImport().bulk_upsert(list(all_subjects))

        book_payload = []
        for doc in valid_docs:
            book_payload.append(
                Book(
                    openlibrary_key=_clear_key(doc["key"]),
                    title=doc["title"],
                    cover_i=doc.get("cover_i"),
                    first_publish_date=_format_data(doc.get("first_publish_year")),
                )
            )

        Book.objects.bulk_create(
            book_payload,
            batch_size=1000,
            update_conflicts=True,
            update_fields=["title", "cover_i", "first_publish_date"],
            unique_fields=["openlibrary_key"],
        )

        saved_books = {
            book.openlibrary_key: book
            for book in Book.objects.filter(
                openlibrary_key__in=[_clear_key(doc["key"]) for doc in valid_docs]
            )
        }

        saved_authors = {
            author.openlibrary_key: author
            for author in Author.objects.filter(
                openlibrary_key__in={
                    _clear_key(key)
                    for doc in valid_docs
                    for key in doc["author_key"]
                }
            )
        }

        saved_subjects = {subject.slug: subject for subject in subjects}

        self._bulk_create_book_relations_from_search(
            valid_docs,
            saved_books=saved_books,
            saved_authors=saved_authors,
            saved_subjects=saved_subjects,
        )

    @staticmethod
    def get_detail_information(data: dict) -> dict:
        excerpts = data.get("excerpts", [])
        excerpt_text = excerpts[0].get("excerpt") if excerpts else None

        raw_description = data.get("description")
        if isinstance(raw_description, dict):
            description = raw_description.get("value", "")
        else:
            description = raw_description or ""

        defaults: dict = {
            "cover_ids": _clean_covers(data.get("covers", [])),
            "description": description,
            "excerpt": excerpt_text,
            "was_requested_detail": True,
            "title": data.get("title"),
        }

        clean_date = _format_data(data.get("first_publish_date", ""))
        if clean_date:
            defaults["first_publish_date"] = clean_date

        return defaults

    @transaction.atomic
    def save_from_detail(self, data: dict | None) -> None:
        if not data:
            return

        defaults = self.get_detail_information(data=data)

        Book.objects.update_or_create(
            openlibrary_key=_clear_key(data["key"]),
            defaults=defaults,
        )

    def _bulk_create_book_relations_from_search(
        self,
        docs: list[dict],
        saved_books: dict[str, Book],
        saved_authors: dict[str, Author],
        saved_subjects: dict[str, Subject],
    ) -> None:
        book_author_through = Book.authors.through
        book_subject_through = Book.subjects.through

        book_author_links = []
        book_subject_links = []

        for doc in docs:
            book = saved_books.get(_clear_key(doc["key"]))
            if not book:
                continue

            for key in doc.get("author_key", []):
                author = saved_authors.get(_clear_key(key))
                if author:
                    book_author_links.append(
                        book_author_through(book_id=book.id, author_id=author.id)
                    )

            for raw_subject in SubjectImport()._resolve(doc.get("subject", [])):
                subject = saved_subjects.get(slugify(raw_subject))
                if subject:
                    book_subject_links.append(
                        book_subject_through(book_id=book.id, subject_id=subject.id)
                    )

        if book_author_links:
            book_author_through.objects.bulk_create(
                book_author_links, batch_size=1000, ignore_conflicts=True
            )

        if book_subject_links:
            book_subject_through.objects.bulk_create(
                book_subject_links, batch_size=1000, ignore_conflicts=True
            )

    @staticmethod
    def _is_valid(data: dict) -> bool:
        required_keys = ["title", "subject", "author_key", "author_name", "key"]
        return all(data.get(key) for key in required_keys)
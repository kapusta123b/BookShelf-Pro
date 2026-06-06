from books.services.subject_map import SUBJECT_MAP


def import_subjects_from_the_map(subject: str) -> str:
    keywords = SUBJECT_MAP.get(subject, [subject])
    parts = [f'subject:"{kw}"' for kw in keywords]
    return ' OR '.join(parts)
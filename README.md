# BookShelf Pro

![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)
![Django Version](https://img.shields.io/badge/django-6.0-green.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-16-336791.svg)
![Open Library](https://img.shields.io/badge/open%20library-API-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Django-based book catalog and personal library platform powered by the Open Library API.

Users can browse books by genre, search by title, author or ISBN, add books to their personal library, track reading status, and leave reviews.

<table>
  <tr>
    <td><img width="310" height="150" alt="BookShelf Pro screenshot" src="" /></td>
    <td><img width="310" height="150" alt="BookShelf Pro screenshot" src="" /></td>
    <td><img width="310" height="150" alt="BookShelf Pro screenshot" src="" /></td>
  </tr>
</table>

---

## Features

- Book catalog with pagination and grid / list view toggle
- Search by title, author, or ISBN
- On-demand book import from Open Library API (Lucene subject queries)
- 19 genre categories with emoji tags and slug-based routing
- Personal library with reading status tracking (Want to Read / Reading / Already Read)
- Status-based catalog filtering (shows only user's books by status)
- Book reviews with spoiler flag and public / private toggle
- User profiles with reading statistics
- Sticky toolbar with working z-index layering
- Filter sidebar with persistent collapse state (localStorage)
- Scroll position restoration across page navigations
- Social authentication via Google and Facebook (django-allauth)
- Email verification on registration
- reCAPTCHA v2 protection on auth forms
- SCSS compiled on the fly via django-sass-processor
- Responsive layout

---

## Stack

- Python 3.13
- Django 6.0
- PostgreSQL 16
- SASS / SCSS
- JavaScript (vanilla)
- django-allauth 65.16
- django-recaptcha 4.1
- django-sass-processor 1.4
- requests (Open Library API)
- psycopg2

---

## Project Structure

```text
BookShelf-Pro
├── backend
│   ├── app                  # Django settings, urls, wsgi
│   ├── books                # Catalog, search, book import, Open Library service
│   │   ├── services
│   │   │   ├── book_import_service.py
│   │   │   ├── searchBook_service.py
│   │   │   └── subject_map.py
│   │   ├── templates
│   │   ├── templatetags
│   │   ├── models.py        # Book, Author, Subject, Review
│   │   └── views.py         # CatalogView (ListView)
│   ├── library              # Personal library, UserBook, AddToLibrary
│   ├── main                 # Landing page
│   ├── users                # Custom user model, profile editing
│   ├── templates            # Base template, allauth overrides
│   ├── static
│   │   └── deps
│   │       ├── css          # SCSS source files
│   │       └── js           # books.js, base.js
│   └── manage.py
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/kapusta123b/BookShelf-Pro.git
cd BookShelf-Pro
```

Create virtual environment:

```bash
python -m venv .venv
```

Activate virtual environment:

Linux:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create environment file:

```bash
cp backend/.env.example backend/.env
```

Edit environment variables:

```bash
nano backend/.env
```

Apply migrations:

```bash
cd backend
python manage.py migrate
```

Create admin user:

```bash
python manage.py createsuperuser
```

Run development server:

```bash
python manage.py runserver
```

Site is available at:

```text
http://localhost:8000
```

---

## Social Authentication

The project supports Google and Facebook authentication through `django-allauth`.

After deployment, create OAuth applications in Google Cloud Console and Facebook Developers.

Required callback URLs:

```text
http://your_domain/accounts/google/login/callback/
http://your_domain/accounts/facebook/login/callback/
```

Then add the providers in Django Admin:

```text
Social Accounts → Social Applications → Add
```

---

## Open Library Integration

Books are fetched from the [Open Library API](https://openlibrary.org/search.json) on demand.

Search by subject uses Lucene OR queries against the `/search.json` endpoint:

```
q=subject:"young adult" OR subject:"young adult fiction" OR subject:"teen fiction"
```

The `SUBJECT_MAP` in `books/services/subject_map.py` maps 19 canonical genres to all their known Open Library subject aliases. Imported books are automatically assigned to the correct genre.

---

## Useful Commands

Open Django shell:

```bash
python manage.py shell
```

Collect static files:

```bash
python manage.py collectstatic
```

---

## License

MIT

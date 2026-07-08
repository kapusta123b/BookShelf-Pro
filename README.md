# BookShelf Pro

![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)
![Django Version](https://img.shields.io/badge/django-6.0-green.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-16-336791.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Django-based book catalog and personal library platform powered by the Open Library API.

Users can browse books by genre, search by title, author or ISBN, add books to their personal library, track reading status, and leave reviews.

<table>
  <tr>
    <td><img width="310" height="150" alt="" src="" /></td>
    <td><img width="310" height="150" alt="" src="" /></td>
    <td><img width="310" height="150" alt="" src="" /></td>
  </tr>
</table>

---

## Features

- Book catalog with pagination and grid / list view toggle
- Search by title, author, or ISBN with on-demand Open Library import
- Personal library
- Book rating
- Book reviews
- User profiles
- Filter sidebar
- Social authentication via Google and Facebook
- Email verification and reCAPTCHA v2

---

## Stack

- Python 3.13 / Django 6.0
- PostgreSQL 16
- SASS / SCSS / JavaScript
- django-allauth, django-recaptcha
- httpx
- psycopg2
---

## Project Structure

```text
BookShelf-Pro
├── backend
│   ├── app          # settings, urls, wsgi
│   ├── books        # catalog, search, Open Library integration
│   │   └── services
│   │       ├── activity.py, catalog.py, client.py
│   │       ├── detail.py, importers.py, rating.py
│   │       └── subject_map.py
│   ├── library      # personal library, UserBook, status management
│   ├── users        # user model, profile, RecentActivity
│   ├── templates
│   └── static
├── requirements.txt
└── README.md
```

---

## Installation

Clone the repository and set up the environment:

```bash
git clone https://github.com/kapusta123b/BookShelf-Pro.git
cd BookShelf-Pro
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Fill `backend/.env` in the required variables::

```env
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1,http://localhost
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASS=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

Apply migrations and run:

```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Site is available at `http://localhost:8000`

---

## Social Authentication

Create OAuth apps in Google Cloud Console and Facebook Developers, then add providers in Django Admin under **Social Accounts → Social Applications**.

Required callback URLs:

```
http://your_domain/accounts/google/login/callback/
http://your_domain/accounts/facebook/login/callback/
```

---

## License

MIT

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    first_name = models.CharField(blank=True, verbose_name='First name')
    last_name = models.CharField(blank=True, verbose_name='Last name')

    description = models.TextField(blank=True, max_length=150, default='')
    avg_rating = models.FloatField(default=0)

    def __str__(self):
        return self.username

    def get_library_data(self, filter: str, page_number: int | str) -> dict:

        all_books = self.library_books.all()
        paginate_books = all_books.tabs_filter(filter).paginate(page_number, per_page=10)
        counts = all_books.get_counts()

        return {
            'books': paginate_books,
            'counts': counts
        }

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

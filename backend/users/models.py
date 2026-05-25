from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    first_name = models.CharField(blank=True, verbose_name='First name')
    last_name = models.CharField(blank=True, verbose_name='Second name')

    description = models.TextField(null=True, blank=False, max_length=150)

    reviews_count = models.IntegerField(default=0)
    books_read = models.IntegerField(default=0)
    reading_now = models.IntegerField(default=0)
    want_to_read = models.IntegerField(default=0)

    avg_rating = models.FloatField(default=0)


    def __str__(self):
        return self.username

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

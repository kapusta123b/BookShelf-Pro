from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    first_name = models.CharField(blank=True, verbose_name='First name')
    last_name = models.CharField(blank=True, verbose_name='Last name')

    description = models.TextField(blank=True, max_length=150, default='')
    avg_rating = models.FloatField(default=0)

    def __str__(self):
        return self.username

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

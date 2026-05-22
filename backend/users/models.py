from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    reviews_count = models.IntegerField(default=0)
    registration_date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.username

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

from django.db import models
from app import settings

from django.core.validators import MinValueValidator, MaxValueValidator


class UserBookQuerySet(models.QuerySet):
    def total_want_read(self):
        return self.filter(status='want_to_read').count()
    
    def total_reading(self):
        return self.filter(status='reading').count()
    
    def total_ulready_read(self):
        return self.filter(status='read').count()

class UserBook(models.Model):
    objects = UserBookQuerySet.as_manager()

    class Status(models.TextChoices):
        WANT_TO_READ = "want_to_read", "Want to read"
        READING = "reading", "Reading"
        READ = "read", "Read"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="library_books",
    )
    book = models.ForeignKey(
        "books.Book",
        on_delete=models.CASCADE,
        related_name="user_entries",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.WANT_TO_READ,
    )
    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5),
        ],
    )

    is_favorite = models.BooleanField(default=False)
    started_at = models.DateField(null=True, blank=True)
    finished_at = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book"],
                name="unique_user_book",
            )
        ]
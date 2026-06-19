from django.utils import timezone

from django.db import models
from django.db.models import Min


from django.conf import settings

from django.core.validators import MinValueValidator, MaxValueValidator


class UserBookQuerySet(models.QuerySet):
    _SORT_MAP = {
        "title": "book__title",
        "rating": "-book__avg_rating",
        "year": "book__first_publish_date",
        "authors": "first_author_name",
        "recently": "-created_at",
    }

    def tabs_filter(self, value: str) -> "UserBookQuerySet":
        if value and value != "all":
            return self.filter(status=value)
        return self

    def sort_by(self, value: str) -> "UserBookQuerySet":
        if not value or value not in self._SORT_MAP:
            return self

        qs = self.select_related("book").prefetch_related("book__authors")

        if value == "authors":
            qs = qs.annotate(first_author_name=Min("book__authors__name"))

        return qs.order_by(self._SORT_MAP[value])

    def get_counts(self) -> dict:
        return self.aggregate(
            total=models.Count("id"),
            want=models.Count("id", filter=models.Q(status="want_to_read")),
            reading=models.Count("id", filter=models.Q(status="reading")),
            read=models.Count("id", filter=models.Q(status="read")),
        )


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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} -- {self.book.title}"

    def change_status(self, status: str) -> bool:

        self.status = status

        if status == self.Status.READING and not self.started_at:
            self.started_at = timezone.now().date()

        elif status == self.Status.READ and not self.finished_at:
            self.finished_at = timezone.now().date()

        self.save(update_fields=["status", "started_at", "finished_at"])

        return True

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book"],
                name="unique_user_book",
            )
        ]

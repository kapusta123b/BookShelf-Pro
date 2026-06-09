from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    first_name = models.CharField(blank=True, verbose_name="First name")
    last_name = models.CharField(blank=True, verbose_name="Last name")

    description = models.TextField(blank=True, max_length=150, default="")
    avg_rating = models.FloatField(default=0)

    def get_library_data(self, page_number: int | str, status_filter: str) -> dict:

        all_books = self.library_books.all()
        paginate_books = all_books.tabs_filter(status_filter).paginate(
            page_number, per_page=10
        )
        counts = all_books.get_counts()

        return {"books": paginate_books, "counts": counts}

    def get_user_activity(self):
        return RecentActivity.objects.filter(user=self).select_related("book")[:10]

    def get_profile_data(self) -> dict:

        all_books = self.library_books
        counts = all_books.get_counts()

        recent_books = list(
            all_books.select_related("book").order_by("updated_at")[:20]
        )

        read = [b for b in recent_books if b.status == "read"][:5]
        want_to_read = [b for b in recent_books if b.status == "want_to_read"][:5]
        reading = [b for b in recent_books if b.status == "reading"][:5]

        return {
            "counts": counts,
            "reading": reading,
            "read": read,
            "want_to_read": want_to_read,
        }

    def __str__(self):
        return self.username

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"


class RecentActivity(models.Model):

    class Action(models.TextChoices):
        ADDED = "added", "Added to library"
        WANT_TO_READ = "want_to_read", "Want to Read"
        READING = "reading", "Started reading"
        READ = "read", "Finished reading"
        RATED = "rated", "Rated"
        REVIEWED = "reviewed", "Reviewed"

    user = models.ForeignKey(
        "users.User", verbose_name="user", on_delete=models.CASCADE
    )
    action = models.CharField(verbose_name="action", choices=Action)
    book = models.ForeignKey(
        "books.Book", verbose_name="book", null=True, on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def icon(self):
        return {
            "added": "plus.svg",
            "want_to_read": "bookmark.svg",
            "reading": "book-open.svg",
            "read": "check.svg",
            "rated": "star-filled.svg",
            "reviewed": "edit.svg",
        }.get(self.action, "plus.svg")

    @property
    def icon_class(self):
        return {
            "added": "added",
            "want_to_read": "added",
            "reading": "read",
            "read": "read",
            "rated": "rated",
            "reviewed": "rated",
        }.get(self.action, "added")

    class Meta:
        db_table = "users_activities"
        ordering = ["-created_at"]

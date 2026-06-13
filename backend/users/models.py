from typing import Any

from django.db import models
from django.db.models import Avg
from django.contrib.auth.models import AbstractUser

from books.models import Review


class User(AbstractUser):
    first_name = models.CharField(blank=True, verbose_name="First name")
    last_name = models.CharField(blank=True, verbose_name="Last name")

    profile_image = models.ImageField(null=True, blank=True, verbose_name="User image")

    description = models.TextField(blank=True, max_length=150, default="")
    avg_rating = models.FloatField(default=0)

    def get_library_data(
        self, page_number: int | str, status_filter: str, sort: str
    ) -> dict:

        all_books = self.library_books.all()
        paginate_books = (
            all_books.tabs_filter(status_filter)
            .sort_by(sort)
            .paginate(page_number, per_page=10)
        )
        counts = all_books.get_counts()

        return {"books": paginate_books, "counts": counts}

    def get_user_activity(self, show_more=False):
        user_activity = RecentActivity.objects.filter(user=self).select_related("book")
        return user_activity[:10] if not show_more else user_activity

    def get_profile_data(self) -> dict:

        all_books = self.library_books
        counts = all_books.get_counts()

        recent_books = list(
            all_books.select_related("book").order_by("-updated_at")[:20]
        )

        recent_reviews = Review.objects.filter(user_book__user=self).select_related(
            "user_book"
        )[:5]

        read = [b for b in recent_books if b.status == "read"][:5]
        want_to_read = [b for b in recent_books if b.status == "want_to_read"][:5]
        reading = [b for b in recent_books if b.status == "reading"][:5]

        return {
            "counts": counts,
            "reading": reading,
            "read": read,
            "want_to_read": want_to_read,
            "reviews": recent_reviews,
        }

    def update_avg_rating(self) -> None:
        avg = self.library_books.filter(rating__isnull=False).aggregate(
            avg=Avg("rating")
        )["avg"]

        self.avg_rating = round(avg, 2) if avg is not None else 0

        self.save(update_fields=["avg_rating"])

    def format_avatar(self) -> str | Any:
        """
        The function is used to format the user's first_name and last_name into a short version
        for example: Jeffrey Epstein will be as J E
        """
        if self.profile_image:
            return self.profile_image.url

        first_name = self.first_name[0].upper() if self.first_name else ""
        last_name = self.last_name[0].upper() if self.last_name else ""

        return f"{first_name} {last_name}".strip()

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
        CHANGE_RATE = "change_rate", "Change rating"
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
            "change_rate": "change-rate.svg",
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
            "change_rate": "change-rate",
        }.get(self.action, "added")

    class Meta:
        db_table = "users_activities"
        ordering = ["-created_at"]

from django.db import models

from django.contrib.auth.models import AbstractUser

import shortuuid

from django.utils import timezone


def generate_short_uuid():
    return shortuuid.ShortUUID().random(length=10)


class User(AbstractUser):
    public_id = models.CharField(
        max_length=10, default=generate_short_uuid, unique=True, editable=False
    )

    first_name = models.CharField(blank=True, verbose_name="First name")
    last_name = models.CharField(blank=True, verbose_name="Last name")

    profile_image = models.ImageField(
        upload_to="avatars/", null=True, blank=True, verbose_name="User image"
    )

    description = models.TextField(blank=True, max_length=150, default="")
    avg_rating = models.FloatField(default=0)

    content_updated_at = models.DateTimeField(default=timezone.now)

    def format_avatar(self) -> str:
        if self.profile_image:
            return self.profile_image.url

        initials = " ".join(
            name[0].upper()
            for name in (self.first_name.strip(), self.last_name.strip())
            if name
        )

        return initials

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
            "change_rate": "edit.svg",

            "create_review": "plus.svg",
            "delete_review": "close.svg",
            "update_review": "edit.svg"
        }.get(self.action, "plus.svg")

    @property
    def icon_class(self):
        return {
            "added": "added",
            "want_to_read": "added",
            "reading": "read",
            "read": "read",

            "rated": "rated",
            "change_rate": "rated",

            "delete_review": "delete-review",
            "update_review": "update-review"

        }.get(self.action, "added")

    class Meta:
        db_table = "users_activities"
        ordering = ["-created_at"]

        indexes = [models.Index(fields=["user", "-created_at"])]

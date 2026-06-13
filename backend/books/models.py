from django.db import models


class Subject(models.Model):
    slug = models.SlugField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = "subject"
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"


class Author(models.Model):
    openlibrary_key = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
    )
    
    name = models.CharField(max_length=255)
    birth_date = models.IntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = "author"
        verbose_name = "Author"
        verbose_name_plural = "Authors"


class BookQuerySet(models.QuerySet):

    def by_category(self, slug: str | None) -> "BookQuerySet":
        if slug and slug != "all":
            return self.filter(subjects__slug=slug)

        return self

    def by_rating(self, value: int | None) -> "BookQuerySet":
        if value and 1 <= value <= 5:
            return self.filter(avg_rating__gte=value).order_by("avg_rating")

        return self

    def by_date(self, from_year: str | None, to_year: str | None) -> "BookQuerySet":
        if from_year and to_year:
            return self.filter(first_publish_date__year__range=(from_year, to_year))

        if from_year:
            return self.filter(first_publish_date__year__gte=from_year)

        if to_year:
            return self.filter(first_publish_date__year__lte=to_year)

        return self


class Book(models.Model):
    objects = BookQuerySet.as_manager()

    openlibrary_key = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
    )
    cover_i = models.PositiveIntegerField(null=True, blank=True)
    cover_ids = models.JSONField(default=list, blank=True)
    title = models.CharField("Title", max_length=255)
    authors = models.ManyToManyField("books.Author", verbose_name="authors")
    first_publish_date = models.DateField(
        verbose_name="First publish year", null=True, blank=True
    )
    subjects = models.ManyToManyField("books.Subject", related_name="books", blank=True)
    description = models.TextField(null=True)
    excerpt = models.TextField(null=True)
    was_requested_detail = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    avg_rating = models.FloatField(default=0)
    rating_count = models.PositiveIntegerField(default=0)

    def get_authors(self) -> list[Author]:
        return self.authors.all()

    def update_avg_rating(self, new_rating: int, old_rating: int | None = None) -> None:
        if old_rating is None:
            self.avg_rating = (self.avg_rating * self.rating_count + new_rating) / (
                self.rating_count + 1
            )
            self.rating_count += 1

        else:

            self.avg_rating = (
                self.avg_rating * self.rating_count - old_rating + new_rating
            ) / self.rating_count

        self.avg_rating = round(self.avg_rating, 2)
        self.save(update_fields=["avg_rating", "rating_count"])

    def remove_rating(self, old_rating: int) -> None:
        if self.rating_count <= 1:
            self.avg_rating = 0
            self.rating_count = 0

        else:

            self.avg_rating = round(
                (self.avg_rating * self.rating_count - old_rating)
                / (self.rating_count - 1),
                2,
            )
            self.rating_count -= 1

        self.save(update_fields=["avg_rating", "rating_count"])

    @property
    def rating_fill_percent(self) -> float:
        return round((self.avg_rating / 5) * 100, 2)

    @property
    def publish_year(self) -> int | None:
        return self.first_publish_date.year if self.first_publish_date else None

    def __str__(self) -> str:
        return f"{self.title} - {self.publish_year}"

    class Meta:
        db_table = "book"
        verbose_name = "Book"
        verbose_name_plural = "Books"


class Review(models.Model):
    user_book = models.OneToOneField(
        "library.UserBook",
        on_delete=models.CASCADE,
        related_name="review",
        null=True,
        blank=True,
    )

    title = models.CharField(max_length=255, blank=True)
    text = models.TextField()
    is_public = models.BooleanField(default=True)
    contains_spoilers = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    @classmethod
    def get_review_object(cls, user):
        return cls.objects.filter(user_book__user=user).select_related('user_book').prefetch_related('user_book__book__authors')

    def __str__(self) -> str:
        return f"Review for {self.user_book.book}"

    class Meta:
        ordering = ["-created_at"]
        db_table = "review"
        verbose_name = "Review"
        verbose_name_plural = "Reviews"

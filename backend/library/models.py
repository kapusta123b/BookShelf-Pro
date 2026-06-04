from django.utils import timezone

from django.db import models
from django.db import transaction

from django.core.paginator import Page, Paginator

from django.conf import settings

from django.core.validators import MinValueValidator, MaxValueValidator


class UserBookQuerySet(models.QuerySet):
    def tabs_filter(self, value: str):
        if value != 'all' and value:
            return self.filter(status=value)

        else:
            return self.all()

    def get_counts(self):
        return self.aggregate(

            total=models.Count('id'),
            want=models.Count('id', filter=models.Q(status='want_to_read')),
            reading=models.Count('id', filter=models.Q(status='reading')),
            read=models.Count('id', filter=models.Q(status='read'))
        
        )
    
    def paginate(self, page_number: str | float | int, per_page: int | str) -> Page:

        paginator = Paginator(self, per_page)

        return paginator.get_page(page_number)

    
    def safe_update_status(self, book_id: int, new_status: str, user):

        with transaction.atomic():
            user_book = (
                self.select_for_update()
                .filter(id=book_id, user=user)
                .first()
            )
            
            if not user_book:
                return None, False
                
            user_book.change_status(new_status)
            
            return user_book, True
    

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
    
    def __str__(self):
        return f'{self.user.username} -- {self.book.title}'
    

    def change_status(self, new_status: str) -> None:

        self.status = new_status
        
        if new_status == self.Status.READING and not self.started_at:
            self.started_at = timezone.now().date()
            
        elif new_status == self.Status.READ and not self.finished_at:
            self.finished_at = timezone.now().date()

        self.save(update_fields=['status', 'started_at', 'finished_at'])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book"],
                name="unique_user_book",
            )
        ]

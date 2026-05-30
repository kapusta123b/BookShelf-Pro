from django.db import models
from django.utils.text import slugify
from app import settings

class Subject(models.Model):
    slug = models.SlugField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=100)
    emoji = models.CharField(null=True)

    def __str__(self):
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

    def __str__(self):
        return self.name
    

    class Meta:
        db_table = 'author'
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'


class BookQuerySet(models.QuerySet):

    def by_category(self, slug):
    
        if slug and slug != 'all':
            return self.filter(subjects__slug=slug)
        
        return self


class Book(models.Model):
    objects = BookQuerySet.as_manager()

    cover_i = models.CharField(null=True)

    title = models.CharField('Title', max_length=100)
    authors = models.ManyToManyField('books.Author', verbose_name='authors')
    first_publish_year = models.IntegerField('First publish year', null=True)
    subjects = models.ManyToManyField('books.Subject', related_name='books', blank=True)

    avg_rating = models.IntegerField(default=0)

    def get_authors(self):
        return ', '.join(author.name for author in self.authors.all())

    def __str__(self):
        return f"{self.title} - {self.first_publish_year}"
    
    class Meta:
        db_table = 'book'
        verbose_name = 'Book'
        verbose_name_plural = 'Books'

    



class Review(models.Model):
    user_book = models.OneToOneField(
        "library.UserBook",
        on_delete=models.CASCADE,
        related_name="review",
        null=True,
        blank=True
    )

    title = models.CharField(max_length=255, blank=True)
    text = models.TextField()

    is_public = models.BooleanField(default=True)
    contains_spoilers = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

        db_table = 'review'
        verbose_name = 'Book'
        verbose_name_plural = 'Books'

    def __str__(self):
        return f"Review for {self.user_book.book}"
    
    
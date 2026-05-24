from django.contrib import admin

from books.models import Author, Book, Subject

# Register your models here.

admin.site.register(Subject)
admin.site.register(Book)
admin.site.register(Author)


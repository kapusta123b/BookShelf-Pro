from django.shortcuts import render
from django.views.generic import ListView

from books.services.book_import_service import BookImportService
from books.services.searchBook_service import BookSearchClient
from books.models import Book


class CatalogView(ListView):
    template_name = 'books/index.html'
    model = Book
    paginate_by = 8
    context_object_name = 'books'

    def get_queryset(self):
        search = self.request.GET.get('search')
        search_by = self.request.GET.get('search_by')

        if search and search_by:
            client = BookSearchClient()
            book_import = BookImportService()

            queryset = self.model.objects.filter(title__icontains=search)

            if not queryset.exists():
                data = client.search_books_by_argument(query=search, argument=search_by, page='1')
                book_import.create_books(json=data)
                queryset = self.model.objects.filter(title__icontains=search)

            return queryset

        
        return super().get_queryset()
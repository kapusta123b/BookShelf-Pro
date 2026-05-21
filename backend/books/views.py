from django.shortcuts import render
from django.views.generic import ListView

from books.models import Book


class CatalogView(ListView):
    template_name = 'books/index.html'
    model = Book
    paginate_by = 8
    context_object_name = 'books'

    def get_queryset(self):
        search = self.request.GET.get('search')
        search_by = self.request.GET.get('search_by')

        queryset = self.model.objects.all()

        if search and search_by:
            pass

        return queryset
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import ListView

from books.services.book_import_service import BookImportService
from books.services.searchBook_service import BookSearchClient
from books.models import Book


class CatalogView(ListView):
    template_name = 'books/index.html'
    model = Book
    paginate_by = 12
    context_object_name = 'books'

    def get(self, request, *args, **kwargs):
        search = request.GET.get('search')
        search_by = request.GET.get('search_by')
        subject = kwargs.get('subject_slug')
        page = request.GET.get('page', 1)

        if search and search_by == 'subject' and subject != 'all':
            client = BookSearchClient()
            book_import = BookImportService()
            
            data = client.search_books_by_argument(query=search, argument=search_by, page=str(page))
            book_import.create_books(json=data)

            url = reverse('books:index', kwargs={'subject_slug': subject})
            return redirect(f'{url}?page={page}')

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        search = self.request.GET.get('search')
        search_by = self.request.GET.get('search_by')
        subject = self.kwargs.get('subject_slug')

        if search and search_by in ('title', 'author', 'isbn'):

            queryset = self.model.objects.filter(title__icontains=search)
            
            if not queryset.exists():
                client = BookSearchClient()
                book_import = BookImportService()
            
                data = client.search_books_by_argument(query=search, argument=search_by, page='1')
                book_import.create_books(json=data)
            
                queryset = self.model.objects.filter(title__icontains=search)
            
            return queryset

        return self.model.objects.by_category(subject)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset_total = super().get_queryset()        
        queryset_current = self.get_queryset()
        

        if self.request.user.is_authenticated:
            context['user_library_ids'] = set(
                self.request.user.library_books.values_list('book_id', flat=True)
            )
        else:
            context['user_library_ids'] = set()

        context['queryset_count_total'] = queryset_total.count()
        context['queryset_count_current'] = queryset_current.count()

        return context
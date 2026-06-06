
from django.shortcuts import redirect

from django.urls import reverse
from django.views.generic import ListView, DetailView

from books.services.client import OpenLibaryClient
from books.services.importers import BookImport

from books.models import Book, Subject


class CatalogView(ListView):
    template_name = 'books/index.html'
    model = Book
    paginate_by = 8
    context_object_name = 'books'
    ordering = ['-date_created']

    def get(self, request, *args, **kwargs):
        #search
        search = request.GET.get('search')
        search_by = request.GET.get('search_by')
        subject = kwargs.get('subject_slug')
        page = request.GET.get('page', 1)

        if search and search_by == 'subject' and subject != 'all':
            client = OpenLibaryClient()
            raw_docs = client.search(
                argument=search_by,
                query=search,
                page=str(page)
            )
            BookImport().save_from_search(
                docs=raw_docs
            )

            url = reverse('books:index', kwargs={'subject_slug': subject,})
            return redirect(f'{url}?page={str(page)}')

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if hasattr(self, '_cached_queryset'):
            return self._cached_queryset

        search = self.request.GET.get('search')
        search_by = self.request.GET.get('search_by')
        subject = self.kwargs.get('subject_slug')
        status = self.request.GET.get('status')

        queryset = self.model.objects
        if search and search_by in ('title', 'author', 'isbn'):

            queryset = queryset.filter(title__icontains=search)

            if not queryset.exists():
                
                client = OpenLibaryClient()

                raw_docs = client.search(
                    argument=search_by,
                    query=search,
                    page='1'
                )

                BookImport().save_from_search(
                    docs=raw_docs
                )

                queryset = queryset.filter(title__icontains=search)

            self._cached_queryset = queryset
            return self._cached_queryset

        if status and status != 'none' and self.request.user.is_authenticated:
            result = (
                queryset.filter(user_entries__user=self.request.user, user_entries__status=status)
                if status != 'all'
                else
                queryset.filter(user_entries__user=self.request.user)
            )

            self._cached_queryset = result
            return self._cached_queryset

        self._cached_queryset = queryset.by_category(subject)
        return self._cached_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['user_library_ids'] = set(
                self.request.user.library_books.values_list('book_id', flat=True)
            )
        else:
            context['user_library_ids'] = set()

        context['queryset_count_total'] = super().get_queryset().count()
        context['queryset_count_current'] = self.get_queryset().count()

        subject_slug = self.kwargs.get('subject_slug')
        if subject_slug and subject_slug != 'all':
            context['current_subject'] = Subject.objects.filter(slug=subject_slug).first()
        else:
            context['current_subject'] = None

        return context
    

class DetailView(DetailView):
    model = Book
    template_name = 'books/detail.html'
    context_object_name = 'book'
    pk_url_kwarg = 'book_id'


    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        if not obj.was_requested_detail:

            client = OpenLibaryClient()
            raw_doc = client.get_detail(obj.openlibrary_key)
            BookImport().save_from_detail(raw_doc)
            
            obj.refresh_from_db()

        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['user_library_ids'] = set(
                self.request.user.library_books.values_list('book_id', flat=True)
            )
        else:
            context['user_library_ids'] = set()
        return context
    
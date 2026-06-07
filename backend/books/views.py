from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin

from books.services.client import OpenLibaryClient
from books.services.importers import BookImport

from books.models import Book, Subject
from library.models import UserBook


class CatalogView(ListView):
    template_name = 'books/index.html'
    model = Book
    paginate_by = 8
    context_object_name = 'books'

    def get(self, request, *args, **kwargs):
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
            BookImport().save_from_search(docs=raw_docs)

            url = reverse('books:index', kwargs={'subject_slug': subject})
            return redirect(f'{url}?page={page}')

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if hasattr(self, '_cached_queryset'):
            return self._cached_queryset

        search = self.request.GET.get('search')
        search_by = self.request.GET.get('search_by')
        subject = self.kwargs.get('subject_slug')
        status = self.request.GET.get('status')
        rating = self.request.GET.get('rating')
        year_from = self.request.GET.get('year_from')
        year_to = self.request.GET.get('year_to')
        sort = self.request.GET.get('sort')
        ordering = sort if sort and sort != 'relevance' else '-date_created'

        rating_value = int(rating) if rating and rating not in ('', 'all') else None

        queryset = self.model.objects

        if search and search_by in ('title', 'author', 'isbn'):
            queryset = queryset.filter(title__icontains=search)

            if not queryset.exists():
                client = OpenLibaryClient()
                raw_docs = client.search(argument=search_by, query=search, page='1')
                BookImport().save_from_search(docs=raw_docs)
                queryset = queryset.filter(title__icontains=search)

            self._cached_queryset = queryset.by_rating(rating_value).by_date(year_from, year_to).order_by(ordering)
            return self._cached_queryset

        if status and status != 'none' and self.request.user.is_authenticated:
            result = (
                queryset.filter(user_entries__user=self.request.user, user_entries__status=status)
                if status != 'all'
                else queryset.filter(user_entries__user=self.request.user)
            )
            self._cached_queryset = result.by_rating(rating_value).by_date(year_from, year_to).order_by(ordering)
            return self._cached_queryset

        self._cached_queryset = (
            queryset
            .by_category(subject)
            .by_rating(rating_value)
            .by_date(year_from, year_to)
            .order_by(ordering)
        )
        return self._cached_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['user_library_ids'] = set(
                self.request.user.library_books.values_list('book_id', flat=True)
            )
        else:
            context['user_library_ids'] = set()

        context['queryset_count_total'] = Book.objects.count()
        context['queryset_count_current'] = self.get_queryset().count()

        subject_slug = self.kwargs.get('subject_slug')
        if subject_slug and subject_slug != 'all':
            context['current_subject'] = Subject.objects.filter(slug=subject_slug).first()
        else:
            context['current_subject'] = None

        return context


class BookDetailView(DetailView):
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
            user_book = self.request.user.library_books.filter(book=self.object).first()
            context['user_rating'] = user_book.rating if user_book else None
            context['user_rating_pct'] = round(((user_book.rating or 0) / 5) * 100) if user_book else 0
        else:
            context['user_library_ids'] = set()
            context['user_rating'] = None
            context['user_rating_pct'] = 0

        return context


class RateBookView(LoginRequiredMixin, View):
    def post(self, request, book_id):
        try:
            rating = int(request.POST.get('rating', 0))
        except (TypeError, ValueError):
            return redirect(request.META.get('HTTP_REFERER', '/'))

        if not 1 <= rating <= 5:
            return redirect(request.META.get('HTTP_REFERER', '/'))

        book = get_object_or_404(Book, id=book_id)
        user_book, _ = UserBook.objects.get_or_create(user=request.user, book=book)

        old_rating = user_book.rating
        user_book.rating = rating
        user_book.save(update_fields=['rating'])

        if old_rating is None:
            book.update_avg_rating(rating)
        else:
            book.update_avg_rating(rating, old_rating=old_rating)

        return redirect(request.META.get('HTTP_REFERER', '/'))

from django.urls import reverse
from django.views.generic import DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

from library.models import UserBook
from users.models import User

class LibraryView(LoginRequiredMixin, DetailView):
    model = User
    pk_url_kwarg = 'user_id'
    template_name = 'library/index.html'
    context_object_name = 'library_user'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_value = self.request.GET.get('filter', 'all')
        
        all_books = self.object.library_books.all()

        context["library_books"] = all_books.tabs_filter(filter_value)
        context["active_filter"] = filter_value
        
        counts = all_books.get_counts()
        
        context["count_total"] = counts['total']
        context["count_reading"] = counts['reading']
        context["count_want_to_read"] = counts['want']
        context["count_finished"] = counts['read']

        return context
    


class AddToLibraryView(LoginRequiredMixin, View):
    def post(self, request, book_id):
        UserBook.objects.get_or_create(
            user=request.user,
            book_id=book_id
        )

        referer = request.META.get('HTTP_REFERER')

        if referer:
            return redirect(referer)

        return redirect(reverse('books:index', kwargs={'subject_slug': 'all'}))


class ChangeStatus(LoginRequiredMixin, View):
    def post(self, request, book_id):
        status = self.request.POST.get('status')

        user_book, _ = UserBook.objects.safe_update_status(book_id, status, request.user)

        referer = request.META.get('HTTP_REFERER')

        if referer:
            return redirect(referer)

        return redirect(reverse('library:index'))
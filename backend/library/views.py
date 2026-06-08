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
        page = self.request.GET.get('page', 1)

        library_data = self.object.get_library_data(page, filter_value)

        context.update({
            "library_books": library_data["books"],
            "active_filter": filter_value,
            "count_total": library_data["counts"]['total'],
            "count_reading": library_data["counts"]['reading'],
            "count_want_to_read": library_data["counts"]['want'],
            "count_finished": library_data["counts"]['read'],
        })
    
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
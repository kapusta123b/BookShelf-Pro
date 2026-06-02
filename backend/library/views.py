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
        context["count_total"] = all_books.count()
        context["count_reading"] = all_books.total_reading()
        context["count_want_to_read"] = all_books.total_want_read()
        context["count_finished"] = all_books.total_already_read()

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

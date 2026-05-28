from django.views.generic import DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect

from library.models import UserBook
from users.models import User

class LibraryView(DetailView):
    model = User
    pk_url_kwarg = 'user_id'
    template_name = 'library/index.html'
    context_object_name = 'library_user'


class AddToLibraryView(LoginRequiredMixin, View):
    def post(self, request, book_id):
        UserBook.objects.get_or_create(
            user=request.user,
            book_id=book_id
        )
        return redirect('books:index')
from django.shortcuts import render
from django.views.generic import DetailView

from users.models import User

class LibraryView(DetailView):
    model = User
    pk_url_kwarg = 'user_id'
    template_name = 'library/index.html'
    context_object_name = 'library_user'

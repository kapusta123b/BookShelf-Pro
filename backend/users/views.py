from django.views.generic import DetailView

from users.models import User

class ProfileView(DetailView):
    model = User
    pk_url_kwarg = 'user_id'
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'
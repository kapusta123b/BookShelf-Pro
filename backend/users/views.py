from django.views.generic import DetailView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from users.models import User
from users.forms import EditProfileForm


class ProfileView(DetailView):
    model = User
    pk_url_kwarg = 'user_id'
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'users/settings.html'


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'users/edit_profile.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse('users:profile', kwargs={'user_id': self.request.user.id})

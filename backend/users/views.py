from django.views.generic import DetailView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from users.models import User
from users.forms import EditProfileForm


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    pk_url_kwarg = 'user_id'
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = self.object.get_profile_data()

        activity = self.object.get_user_activity()

        context.update({
            "activity": activity,
            "library_books": data['reading'],
            "read_books_preview": data['read'],
            "want_to_read_preview": data['want_to_read'],
            "count_total": data['counts']['total'],
            "count_reading": data['counts']['reading'],
            "count_want_to_read": data['counts']['want'],
            "count_finished": data['counts']['read'],
        })

        return context
    


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

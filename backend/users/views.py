from django.views.generic import DetailView, UpdateView, TemplateView

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib import messages

from django.urls import reverse

from users.selectors import get_profile_data, get_user_activity
from users.models import User
from users.forms import EditProfileForm

from utils.helpers import get_user_content_timestamp

class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "users/profile.html"
    context_object_name = "profile_user"
    slug_field = "public_id"
    slug_url_kwarg = "public_id"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        show_more = True if "show_more" in self.request.GET else False

        user_ts = get_user_content_timestamp(self.object)

        data = get_profile_data(self.object, user_ts)
        
        activity = get_user_activity(self.object, user_ts, show_more)

        context.update(
            {
                "activity": activity,
                "library_books": data["reading"],
                "read_books_preview": data["read"],
                "want_to_read_preview": data["want_to_read"],
                "count_total": data["counts"]["total"],
                "count_reading": data["counts"]["reading"],
                "count_want_to_read": data["counts"]["want"],
                "count_finished": data["counts"]["read"],
                "reviews": data["reviews"],
            }
        )

        return context


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = "users/settings.html"


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = "users/edit_profile.html"

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        messages.success(self.request, f"{self.request.user.get_username()}, your profile updated.")

        return reverse("users:profile", kwargs={"public_id": self.object.public_id})

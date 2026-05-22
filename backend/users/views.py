from django.shortcuts import render
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin

from users.forms import UserLoginForm


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = UserLoginForm



def register_view(request):
    return render(request, 'users/registration.html')


def profile_view(request):
    return render(request, 'users/profile.html')

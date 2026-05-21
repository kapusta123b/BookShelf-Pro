from django.shortcuts import render


def login_view(request):
    return render(request, 'users/login.html')


def register_view(request):
    return render(request, 'users/registration.html')


def profile_view(request):
    return render(request, 'users/profile.html')

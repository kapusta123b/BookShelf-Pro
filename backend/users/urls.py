from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'users'

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.LogoutView.as_view(), name='logout')
]

from django.urls import path
from . import views
from allauth.account.views import LoginView, SignupView, LogoutView

app_name = "users"

urlpatterns = [
    path("profile/<str:public_id>", views.ProfileView.as_view(), name="profile"),
    path("settings/", views.SettingsView.as_view(), name="settings"),
    path("edit-profile/", views.EditProfileView.as_view(), name="edit_profile"),
    path("login/", LoginView.as_view(), name="login"),
    path("register/", SignupView.as_view(), name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
]

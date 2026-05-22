from django.contrib.auth.forms import (
    AuthenticationForm,
    UserChangeForm,
    UserCreationForm,
)

from users.models import User


class UserLoginForm(AuthenticationForm):

    class Meta:
        model = User
        fields = [
            'sername', 'password'
        ]
from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha import widgets

from users.models import User
from allauth.account.forms import LoginForm, SignupForm


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3, "maxlength": 150}),
        }


class UserLoginForm(LoginForm):
    captcha = ReCaptchaField(
        widget=widgets.ReCaptchaV2Checkbox(
            attrs={
                "data-theme": "light",
            }
        )
    )


class UserSignUpForm(SignupForm):
    first_name = forms.CharField(max_length=30, required=False, label="First name")
    last_name = forms.CharField(max_length=30, required=False, label="Last name")
    captcha = ReCaptchaField(
        widget=widgets.ReCaptchaV2Checkbox(attrs={"data-theme": "light"})
    )

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        user.save()

        return user

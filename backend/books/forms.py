from django_recaptcha.fields import ReCaptchaField
from django_recaptcha import widgets

from django.shortcuts import get_object_or_404

from django import forms

from library.models import UserBook
from books.models import Review


class CreateReviewForm(forms.ModelForm):
    captcha = ReCaptchaField(
        widget=widgets.ReCaptchaV2Checkbox(
            attrs={
                "data-theme": "light",
            }
        )
    )

    class Meta:
        model = Review
        fields = ["title", "text", "is_public", "contains_spoilers"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3, "maxlength": 1000}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.opl_key = kwargs.pop("opl_key", None)
        super().__init__(*args, **kwargs)


    def save(self, commit=True):
        review = super().save(commit=False)

        user_book = get_object_or_404(UserBook, book__openlibrary_key=self.opl_key, user=self.user)
    
        review.user_book = user_book

        if commit:
            review.save()

        return review


class UpdateReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ["title", "text", "is_public", "contains_spoilers"]

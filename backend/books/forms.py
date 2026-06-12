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
        self.book_id = kwargs.pop("book_id", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        review = super().save(commit=False)

        user_book = get_object_or_404(UserBook, book_id=self.book_id, user=self.user)

        review.user_book = user_book

        if commit:
            review.save()

        return review

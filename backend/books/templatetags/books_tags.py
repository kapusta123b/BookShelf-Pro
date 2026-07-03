from django import template
from django.utils.safestring import mark_safe
from django.templatetags.static import static

import markdown as md

from books.models import Subject

register = template.Library()

COVER_BASE_URL = "https://covers.openlibrary.org/b/id/"


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context["request"].GET.copy()
    for kwarg, value in kwargs.items():
        query[kwarg] = value

    return f"?{query.urlencode()}"


@register.simple_tag()
def tag_subjects():
    return Subject.objects.all()


@register.simple_tag()
def get_cover(letter, cover):
    if not cover:
        return static("deps/svg/no-image.jpg")

    return f"{COVER_BASE_URL}{cover}-{letter}.jpg"


@register.filter(name="markdown")
def render_markdown(value):
    if not value:
        return ""

    result = md.markdown(
        value,
        extensions=["nl2br"],
    )

    return mark_safe(result)

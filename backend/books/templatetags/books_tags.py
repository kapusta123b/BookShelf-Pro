from django import template
from django.utils.safestring import mark_safe

import markdown as md

from library.models import UserBook
from books.models import Subject

register = template.Library()



@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    query = context['request'].GET.copy()
    for kwarg, value in kwargs.items():
        query[kwarg] = value
    
    return query.urlencode()

@register.simple_tag()
def tag_subjects():
    return Subject.objects.all()

@register.filter(name='markdown')
def render_markdown(value):
    if not value:
        return ''
    result = md.markdown(
        value,
        extensions=['nl2br'],
    )
    return mark_safe(result)
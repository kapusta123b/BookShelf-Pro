from django import template

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
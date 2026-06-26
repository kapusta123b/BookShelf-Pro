from django.core.paginator import Page, Paginator, InvalidPage
from django.db.models import QuerySet
from typing import Union

Numeric = Union[str, int]


def paginate(queryset: QuerySet, page_number: Numeric, per_page: Numeric) -> Page:
    try:
        per_page = int(per_page)

    except (ValueError, TypeError):
        per_page = 10

    paginator = Paginator(queryset, per_page)
    
    try:
        return paginator.page(page_number)
    

    except InvalidPage:

        return paginator.page(1)

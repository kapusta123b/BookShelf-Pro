from django.core.paginator import Page, Paginator, InvalidPage
from django.db.models import QuerySet
from typing import Union

from users.models import User

from django.utils import timezone

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


def update_user_library_timestamp(user) -> None:
    User.objects.filter(id=user.id).update(content_updated_at=timezone.now())


def get_user_content_timestamp(user) -> float:
    ts = int((user.content_updated_at or timezone.now()).timestamp())
    
    return ts

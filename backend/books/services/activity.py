from utils.helpers import update_user_library_timestamp
from users.models import RecentActivity, User

from django.db import transaction


@transaction.atomic
def add_activity(user: User, action: str, book_id: int, rating: int = 0) -> None:
    RecentActivity.objects.create(
        user=user, book_id=book_id, rating=rating, action=action
    )

    update_user_library_timestamp(user)

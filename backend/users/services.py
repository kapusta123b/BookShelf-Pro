from users.models import User
from django.db.models import Avg



def update_user_avg_rating(user: User) -> None:
    """
    Update average user rating
    """

    avg = user.library_books.filter(rating__isnull=False).aggregate(
        avg=Avg("rating")
    )["avg"]

    user.avg_rating = round(avg, 2) if avg is not None else 0

    user.save(update_fields=["avg_rating"])
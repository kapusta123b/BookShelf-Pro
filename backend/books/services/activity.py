


from users.models import RecentActivity


def add_activity(user: dict, action: str, book_id: int, rating: int = 0) -> None:
    try:
        RecentActivity.objects.create(
            user=user,
            book_id=book_id,
            rating=rating,
            action=action
        )
    except Exception:
        return None
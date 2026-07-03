from books.models import Review
from users.models import RecentActivity, User


def get_user_activity(user: User, show_more: bool = False):
    """
    Return user activities, limited to 10 items unless show_more is True.
    """

    user_activity = RecentActivity.objects.filter(user=user).select_related("book")
    return user_activity[:10] if not show_more else user_activity


def get_profile_data(user: User) -> dict:
    """
    Return aggregated stats and lists for the user profile.
    """

    all_books = user.library_books.all()
    base_qs = (
        all_books.select_related("book")
        .prefetch_related("book__authors")
        .order_by("-updated_at")
    )

    return {
        "counts": all_books.get_counts(),
        "reading": base_qs.filter(status="reading")[:5],
        "read": base_qs.filter(status="read")[:5],
        "want_to_read": base_qs.filter(status="want_to_read")[:5],
        "reviews": Review.objects.filter(user_book__user=user)
        .select_related("user_book__book")
        .order_by("-created_at")[:5],
    }

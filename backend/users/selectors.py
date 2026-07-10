from books.models import Review

from users.models import RecentActivity, User

from django.core.cache import cache


def get_user_activity(user: User, ts: float, show_more: bool = False):
    """
    Return user activities, limited to 10 items unless show_more is True.
    """
    cache_key = f"activity:user={user.public_id}:ts{ts}:more{show_more}"

    def fetch_activity():
        user_activity = RecentActivity.objects.filter(user=user).select_related("book")
        if not show_more:
            return list(user_activity[:10])

        return list(user_activity)

    return cache.get_or_set(cache_key, fetch_activity, timeout=86400)


def get_profile_data(user: User, ts: float) -> dict:
    """
    Return aggregated stats and lists for the user profile.
    """

    cache_key = f"profile:user={user.public_id}:ts{ts}"

    def fetch_library_data():
        all_books = user.library_books.all()
        counts = all_books.get_counts()
        base_qs = (
            all_books.select_related("book")
            .prefetch_related("book__authors")
            .order_by("-updated_at")
        )

        return {
            "reading": list(base_qs.filter(status="reading")[:5]),
            "read": list(base_qs.filter(status="read")[:5]),
            "want_to_read": list(base_qs.filter(status="want_to_read")[:5]),
            "reviews": list(
                Review.objects.filter(user_book__user=user)
                .select_related("user_book__book")
                .order_by("-created_at")[:5]
            ),
            "counts": counts,
        }

    data = cache.get_or_set(cache_key, fetch_library_data, timeout=86400)

    return data

from books.models import Review

from users.models import User


def get_library_data(
        user: User, status_filter: str, sort: str, reverse_sort: bool
    ) -> dict:
        all_books = user.library_books.all()
        counts = all_books.get_counts() 

        reviews = (
            Review.objects.filter(user_book__user=user)
            .select_related("user_book__book")
            .prefetch_related("user_book__book__authors")
            .order_by("-created_at")
        )

        reviews_ids = set(reviews.values_list("user_book_id", flat=True))

        queryset = (
            all_books.select_related("review").tabs_filter(status_filter).sort_by(sort)
        )

        if reverse_sort:
            queryset = queryset.reverse()

        return {
            "reviews_ids": reviews_ids,
            "reviews": reviews,
            "books": queryset,
            "counts": counts,
        }
from django.urls import path
from . import views

app_name = "books"

urlpatterns = [
    path("rate/<int:book_id>", views.RateBookView.as_view(), name="rate"),
    path("<slug:subject_slug>/", views.CatalogView.as_view(), name="index"),
    path(
        "<slug:subject_slug>/<int:book_id>",
        views.BookDetailView.as_view(),
        name="book_detail",
    ),
    path(
        "<slug:subject_slug>/authors/<int:author_id>",
        views.AuthorDetailView.as_view(),
        name="author_detail",
    ),
    path(
        "<int:book_id>/create-review",
        views.CreateReviewView.as_view(),
        name="create_review",
    ),
    path(
        "<int:review_id>/update-review",
        views.UpdateReviewView.as_view(),
        name="update_review",
    ),
    path(
        "<int:review_id>/delete-review",
        views.DeleteReviewView.as_view(),
        name="delete_review",
    ),
]

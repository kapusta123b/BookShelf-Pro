from django.urls import path
from . import views

app_name = "books"

urlpatterns = [
    path("<slug:subject_slug>/", views.CatalogView.as_view(), name="index"),

    path("<slug:subject_slug>/<slug:opl_key>", views.BookDetailView.as_view(), name="book_detail"),

    path("<slug:subject_slug>/authors/<slug:opl_key>", views.AuthorDetailView.as_view(), name="author_detail"),

    path("<slug:opl_key>/create-review", views.CreateReviewView.as_view(), name="create_review"),

    path("<int:review_id>/update-review", views.UpdateReviewView.as_view(), name="update_review"),

    path("<int:review_id>/delete-review", views.DeleteReviewView.as_view(), name="delete_review"),

    path("rate/<slug:opl_key>", views.RateBookView.as_view(), name="rate"),
]

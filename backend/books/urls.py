from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('<slug:subject_slug>/', views.CatalogView.as_view(), name='index'),
    path('<slug:subject_slug>/<int:book_id>', views.DetailView.as_view(), name='detail'),

]

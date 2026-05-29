from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('<slug:subject_slug>/', views.CatalogView.as_view(), name='index'),
]

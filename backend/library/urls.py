from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('<int:user_id>', views.LibraryView.as_view(), name='index'),
]

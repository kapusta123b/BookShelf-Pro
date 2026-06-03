from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('<int:user_id>', views.LibraryView.as_view(), name='index'),
    path('add_to_library/<int:book_id>', views.AddToLibraryView.as_view(), name='add_to_library'),
    path('change_status/<int:book_id>', views.ChangeStatus.as_view(), name='change_status')
]

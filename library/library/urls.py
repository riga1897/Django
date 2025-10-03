from django.urls import path

from .apps import LibraryConfig
from .views import BooksListView, BookDetailView, BookCreateView, BookUpdateView, BookDeleteView, \
    AuthorCreateView, AuthorUpdateView, AuthorListView  # , books_list, \
# book_detail

app_name = LibraryConfig.name

urlpatterns = [
    # path("books_list/", books_list, name="books_list"),
    # path("book_detail/<int:book_id>", book_detail, name="book_detail"),
    path('authors', AuthorListView.as_view(), name='authors_list'),
    path('author/new', AuthorCreateView.as_view(), name='author_create'),
    path('author/update/<int:pk>', AuthorUpdateView.as_view(), name='author_update'),

    path('books/', BooksListView.as_view(), name='books_list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('books/new/', BookCreateView.as_view(), name='book_create'),
    path('books/<int:pk>/update/', BookUpdateView.as_view(), name='book_update'),
    path('books/<int:pk>/delete/', BookDeleteView.as_view(), name='book_delete'),
]

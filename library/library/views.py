from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .forms import AuthorForm, BookForm
from .models import Author, Book


class AuthorListView(LoginRequiredMixin, ListView):
    model = Author
    form_class = AuthorForm
    template_name = "library/authors_list.html"
    context_object_name = "authors"


class AuthorDetailView(LoginRequiredMixin, DetailView):
    model = Author
    template_name = "library/author_detail.html"
    context_object_name = "author"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["books_count"] = self.object.books.count()
        return context


class AuthorCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Author
    fields = ["first_name", "last_name", "birth_date"]
    template_name = "library/author_form.html"
    success_url = reverse_lazy("library:authors_list")


class AuthorUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ["first_name", "last_name", "birth_date"]
    template_name = "library/author_form.html"
    success_url = reverse_lazy("library:authors_list")


class AuthorDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Author
    template_name = "library/author_confirm_delete.html"
    success_url = reverse_lazy("library:authors_list")


class BooksListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Book
    template_name = "library/books_list.html"
    context_object_name = "books"
    permission_required = "library.view_book"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(publication_date__year__gt=1900)


class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = "library/book_detail.html"
    context_object_name = "book"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["author_books_count"] = Book.objects.filter(author=self.object.author).count()
        return context


class BookCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Book
    # fields = ['title', 'publication_date', 'author']
    form_class = BookForm
    template_name = "library/book_form.html"
    success_url = reverse_lazy("library:books_list")
    permission_required = "library.add_book"


class BookUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Book
    # fields = ['title', 'publication_date', 'author']
    form_class = BookForm
    template_name = "library/book_form.html"
    success_url = reverse_lazy("library:books_list")
    permission_required = "library.change_book"


class BookDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Book
    template_name = "library/book_confirm_delete.html"
    success_url = reverse_lazy("library:books_list")
    permission_required = "library.delete_book"


# def books_list(request):
#     books = Book.objects.all()
#     context = {'books': books}
#     return render(request, 'library/books_list.html', context)
#
#
# def book_detail(request, book_id):
#     book = Book.objects.get(id=book_id)
#     context = {'book': book}
#     return render(request, 'library/book_detail.html', context)

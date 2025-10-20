from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.http import HttpResponseForbidden

from .forms import AuthorForm, BookForm
from .models import Author, Book
from .services import BookService

from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache


class ReviewBookView(LoginRequiredMixin, View):
    @staticmethod
    def post(request, pk):
        book = get_object_or_404(Book, id=pk)

        if not request.user.has_perm("library.can_review_book"):
            result = HttpResponseForbidden("У вас нет права для рецензирования книги")
        else:
            book.review = request.POST.get("library:book_review")
            book.save()

            result = redirect("library:book_detail", pk)

        return result


class RecommendBookView(LoginRequiredMixin, View):
    @staticmethod
    def post(request, pk):
        book = get_object_or_404(Book, id=pk)

        if not request.user.has_perm("library.can_recommend_book"):
            result = HttpResponseForbidden("У вас нет права для рекомендации книги")
        else:
            book.review = request.POST.get("library:book_review")
            book.save()

            result = redirect("library:book_detail", pk)

        return result


class AuthorListView(LoginRequiredMixin, ListView):
    model = Author
    form_class = AuthorForm
    template_name = "library/authors_list.html"
    context_object_name = "authors"

    def get_queryset(self):
        queryset = cache.get("authors_queryset")
        if not queryset:
            queryset = super().get_queryset()
            cache.set("authors_queryset", queryset)
        return queryset

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


@method_decorator(cache_page(60 * 15), name="dispatch")
class BooksListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Book
    template_name = "library/books_list.html"
    context_object_name = "books"
    permission_required = "library.view_book"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(publication_date__year__gt=1900)


@method_decorator(cache_page(60 * 15), name="dispatch")
class BookDetailView(DetailView):
    model = Book
    template_name = 'library/book_detail.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        # Получаем стандартный контекст данных из родительского класса
        context = super().get_context_data(**kwargs)
        # Получаем ID книги из объекта
        book_id = self.object.id
        # Добавляем в контекст средний рейтинг и статус популярности книги
        context['average_rating'] = BookService.calculate_average_rating(book_id)
        context['is_popular'] = BookService.is_popular(book_id)
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

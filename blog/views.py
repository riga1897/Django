from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from marketplace.views import ModalLoginRequiredMixin

from .forms import BlogPostForm
from .models import BlogPost


class BlogPostListView(ListView):  # type: ignore[type-arg]
    model = BlogPost
    template_name = "blog/blogpost_list.html"
    context_object_name = "posts"

    def get_queryset(self) -> QuerySet[BlogPost]:  # type: ignore[override]
        """
        Фильтрация постов:
        - Неавторизованные: только опубликованные
        - Staff/контент-менеджеры: все посты
        - Обычные пользователи: опубликованные ИЛИ свои собственные
        """
        user = self.request.user
        if user.is_authenticated and (
            user.is_staff or user.groups.filter(name="Контент-менеджер").exists()
        ):  # type: ignore[attr-defined]
            # Staff или контент-менеджеры видят все посты
            return BlogPost.objects.all().order_by("-created_at")  # type: ignore[attr-defined]
        elif user.is_authenticated:
            # Авторизованные пользователи видят опубликованные ИЛИ свои собственные
            return BlogPost.objects.filter(  # type: ignore[attr-defined]
                Q(is_published=True) | Q(owner=user)
            ).order_by("-created_at")
        else:
            # Неавторизованные видят только опубликованные
            return BlogPost.objects.filter(is_published=True).order_by("-created_at")  # type: ignore[attr-defined]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            # Проверяем, является ли пользователь контент-менеджером
            context["is_manager"] = (
                user.is_staff or user.groups.filter(name="Контент-менеджер").exists()
            )  # type: ignore[attr-defined]
        else:
            context["is_manager"] = False
        return context


class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = "blog/blogpost_detail.html"
    context_object_name = "post"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        pk = kwargs["pk"]
        obj = get_object_or_404(BlogPost, pk=pk)
        BlogPost.objects.filter(pk=obj.pk).update(views_count=F("views_count") + 1)  # type: ignore[attr-defined]
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            # Проверяем, является ли пользователь контент-менеджером
            context["is_manager"] = user.is_staff or user.groups.filter(name="Контент-менеджер").exists()  # type: ignore[attr-defined]
        else:
            context["is_manager"] = False
        return context


class BlogPostCreateView(ModalLoginRequiredMixin, CreateView):  # type: ignore[type-arg]
    model = BlogPost
    form_class = BlogPostForm
    template_name = "blog/blogpost_form.html"
    success_url = reverse_lazy("blog:post_list")

    def get_form(self, form_class: Any = None) -> Any:
        """Скрыть поле owner от обычных пользователей"""
        form = super().get_form(form_class)
        user = self.request.user
        # Только контент-менеджеры могут выбирать владельца
        if not (user.is_staff or user.groups.filter(name="Контент-менеджер").exists()):  # type: ignore[attr-defined]
            form.fields.pop("owner", None)
        return form

    def form_valid(self, form: Any) -> HttpResponse:  # type: ignore[override]
        # Назначаем владельца перед сохранением, если он не указан
        if not form.cleaned_data.get("owner"):
            form.instance.owner = self.request.user
        return super().form_valid(form)


class BlogPostUpdateView(ModalLoginRequiredMixin, UpdateView):  # type: ignore[type-arg]
    model = BlogPost
    form_class = BlogPostForm
    template_name = "blog/blogpost_form.html"

    def get_form(self, form_class: Any = None) -> Any:
        """Контент-менеджер видит только owner, обычный владелец - все поля кроме owner"""
        form = super().get_form(form_class)
        user = self.request.user
        is_owner = self.object.owner == user
        is_manager = user.is_staff or user.groups.filter(name="Контент-менеджер").exists()  # type: ignore[attr-defined]

        if is_manager:
            # Контент-менеджер может изменять только владельца (даже если он сам владелец)
            fields_to_remove = [field for field in form.fields if field != "owner"]
            for field in fields_to_remove:
                form.fields.pop(field)
        elif is_owner:
            # Обычный владелец (не контент-менеджер) может редактировать все поля, кроме owner
            form.fields.pop("owner", None)

        return form

    def get_queryset(self) -> QuerySet[BlogPost]:  # type: ignore[override]
        """Владелец может редактировать свой пост, контент-менеджер - любой"""
        user = self.request.user
        if user.is_staff or user.groups.filter(name="Контент-менеджер").exists():  # type: ignore[attr-defined]
            # Контент-менеджеры видят все посты
            return BlogPost.objects.all()  # type: ignore[attr-defined]
        else:
            # Обычный пользователь видит только свои
            return BlogPost.objects.filter(owner=user)  # type: ignore[attr-defined,misc]

    def get_success_url(self) -> str:
        return str(reverse_lazy("blog:post_detail", kwargs={"pk": self.object.pk}))


class BlogPostDeleteView(ModalLoginRequiredMixin, DeleteView):  # type: ignore[type-arg]
    model = BlogPost
    template_name = "blog/blogpost_confirm_delete.html"
    success_url = reverse_lazy("blog:post_list")

    def get_queryset(self) -> QuerySet[BlogPost]:  # type: ignore[override]
        """Владелец ИЛИ контент-менеджер с группой 'Контент-менеджер' может удалить"""
        user = self.request.user
        if user.groups.filter(name="Контент-менеджер").exists():  # type: ignore[attr-defined]
            # Контент-менеджер видит все посты
            return BlogPost.objects.all()  # type: ignore[attr-defined]
        else:
            # Обычный пользователь видит только свои
            return BlogPost.objects.filter(owner=user)  # type: ignore[attr-defined,misc]


class BlogPostTogglePublishView(LoginRequiredMixin, View):
    """Переключение статуса публикации поста (для владельца или контент-менеджера)"""

    def post(self, request: Any, pk: int) -> HttpResponse:
        post = get_object_or_404(BlogPost, pk=pk)

        # Проверка: пользователь должен быть владельцем ИЛИ иметь разрешение контент-менеджера
        user = request.user
        is_owner = post.owner == user
        is_manager = user.has_perm("blog.can_unpublish_post")

        if not (is_owner or is_manager):
            from django.core.exceptions import PermissionDenied

            raise PermissionDenied("У вас нет прав для изменения статуса публикации этого поста")

        post.is_published = not post.is_published
        post.save()
        return redirect("blog:post_list")

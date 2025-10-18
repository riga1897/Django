from typing import Any

from django.db.models import F, QuerySet
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from marketplace.views import ModalLoginRequiredMixin

from .models import BlogPost


class BlogPostListView(ListView):  # type: ignore[type-arg]
    model = BlogPost
    template_name = "blog/blogpost_list.html"
    context_object_name = "posts"

    def get_queryset(self) -> QuerySet[BlogPost]:
        show_drafts = self.request.GET.get("show_drafts")

        if show_drafts:
            return BlogPost.objects.all().order_by("-created_at")
        else:
            return BlogPost.objects.filter(is_published=True).order_by("-created_at")


class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = "blog/blogpost_detail.html"
    context_object_name = "post"

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        pk = kwargs["pk"]
        obj = get_object_or_404(BlogPost, pk=pk)
        BlogPost.objects.filter(pk=obj.pk).update(views_count=F("views_count") + 1)
        return super().get(request, *args, **kwargs)


class BlogPostCreateView(ModalLoginRequiredMixin, CreateView):  # type: ignore[type-arg]
    model = BlogPost
    template_name = "blog/blogpost_form.html"
    fields = ["title", "content", "preview", "is_published"]
    success_url = reverse_lazy("blog:post_list")

    def form_valid(self, form: Any) -> HttpResponse:
        form.instance.owner = self.request.user
        return super().form_valid(form)


class BlogPostUpdateView(ModalLoginRequiredMixin, UpdateView):  # type: ignore[type-arg]
    model = BlogPost
    template_name = "blog/blogpost_form.html"
    fields = ["title", "content", "preview", "is_published"]

    def get_queryset(self) -> QuerySet[BlogPost]:
        """Только владелец может редактировать пост"""
        return BlogPost.objects.filter(owner=self.request.user)

    def get_success_url(self) -> str:
        return str(reverse_lazy("blog:post_detail", kwargs={"pk": self.object.pk}))


class BlogPostDeleteView(ModalLoginRequiredMixin, DeleteView):  # type: ignore[type-arg]
    model = BlogPost
    template_name = "blog/blogpost_confirm_delete.html"
    success_url = reverse_lazy("blog:post_list")

    def get_queryset(self) -> QuerySet[BlogPost]:
        """Владелец ИЛИ контент-менеджер с группой 'Контент-менеджер' может удалить"""
        user = self.request.user
        if user.groups.filter(name="Контент-менеджер").exists():
            # Контент-менеджер видит все посты
            return BlogPost.objects.all()
        else:
            # Обычный пользователь видит только свои
            return BlogPost.objects.filter(owner=user)


class BlogPostTogglePublishView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Переключение статуса публикации поста (только для контент-менеджеров)"""

    permission_required = "blog.can_unpublish_post"

    def post(self, request: Any, pk: int) -> HttpResponse:
        post = get_object_or_404(BlogPost, pk=pk)
        post.is_published = not post.is_published
        post.save()
        return redirect("blog:post_list")

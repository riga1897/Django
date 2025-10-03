from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import BlogPost


class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blog/blogpost_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        show_drafts = self.request.GET.get('show_drafts')

        if show_drafts:
            return BlogPost.objects.all().order_by('-created_at')
        else:
            return BlogPost.objects.filter(is_published=True).order_by('-created_at')


class BlogPostDetailView(UserPassesTestMixin, DetailView):
    model = BlogPost
    template_name = 'blog/blogpost_detail.html'
    context_object_name = 'post'

    def test_func(self):
        post = self.get_object()
        return post.is_published or (self.request.user.is_authenticated and (
                    self.request.user.is_staff or self.request.user.is_superuser))

    def get(self, request, *args, **kwargs):
        pk = kwargs['pk']
        # Явно получаем объект или 404
        obj = get_object_or_404(BlogPost, pk=pk)
        BlogPost.objects.filter(pk=obj.pk).update(views_count=F('views_count') + 1)
        return super().get(request, *args, **kwargs)


class BlogPostCreateView(CreateView):
    model = BlogPost
    template_name = 'blog/blogpost_form.html'
    fields = ['title', 'content', 'preview', 'is_published']
    success_url = reverse_lazy('blog:post_list')


class BlogPostUpdateView(UpdateView):
    model = BlogPost
    template_name = 'blog/blogpost_form.html'
    fields = ['title', 'content', 'preview', 'is_published']

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.pk})


class BlogPostDeleteView(DeleteView):
    model = BlogPost
    template_name = 'blog/blogpost_confirm_delete.html'
    success_url = reverse_lazy('blog:post_list')

from django.urls import path

from . import views
from .apps import BlogConfig

app_name = BlogConfig.name

urlpatterns = [
    path("", views.BlogPostListView.as_view(), name="post_list"),
    path("post/<int:pk>/", views.BlogPostDetailView.as_view(), name="post_detail"),
    path("post/create/", views.BlogPostCreateView.as_view(), name="post_create"),
    path("post/<int:pk>/update/", views.BlogPostUpdateView.as_view(), name="post_update"),
    path("post/<int:pk>/delete/", views.BlogPostDeleteView.as_view(), name="post_delete"),
    path("post/<int:pk>/toggle-publish/", views.BlogPostTogglePublishView.as_view(), name="post_toggle_publish"),
]

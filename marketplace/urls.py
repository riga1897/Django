from django.urls import path

from marketplace.apps import MarketplaceConfig

from . import views

app_name = MarketplaceConfig.name

urlpatterns = [
    path("", views.ProductsListView.as_view(), name="products_list"),
    path("product/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("product/create/", views.ProductCreateView.as_view(), name="product_create"),
    path("product/<int:pk>/update/", views.ProductUpdateView.as_view(), name="product_update"),
    path("product/<int:pk>/delete/", views.ProductDeleteView.as_view(), name="product_delete"),
    path("product/<int:pk>/toggle-publish/", views.ProductTogglePublishView.as_view(), name="product_toggle_publish"),
    path("contacts/", views.ContactsView.as_view(), name="contacts"),
]

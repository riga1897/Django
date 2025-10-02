from django.urls import path

from marketplace.apps import MarketplaceConfig
from . import views

app_name = MarketplaceConfig.name

urlpatterns = [
    path("", views.ProductsListView.as_view(), name="products_list"),
    path("product_detail/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("contacts/", views.ContactsView.as_view(), name="contacts"),
]

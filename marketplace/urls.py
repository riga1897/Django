from django.urls import path
from marketplace.apps import MarketplaceConfig
from . import views


app_name = MarketplaceConfig.name

urlpatterns = [
    path('', views.products_list, name="products_list"),
    path("product_detail/<int:product_id>/", views.product_detail, name="product_detail"),
]

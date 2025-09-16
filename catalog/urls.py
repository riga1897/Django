from django.urls import path

from catalog.apps import CatalogConfig
from catalog.views import contacts, home

app_name = CatalogConfig.name

urlpatterns = [
    path("/", home, name="home"),
    path("home/", home, name="home"),  # можно сделать index
    path("contacts/", contacts, name="contacts"),
    path("", home, name="home"),
]

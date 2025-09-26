from django.urls import path

from . import views

app_name = "students"

urlpatterns = [
    path("show_data/", views.show_data, name="show_data"),
    path("submit_data/", views.submit_data, name="submit_data"),
    path("item/<int:item_id>", views.show_item, name="show_item"),
    # path("list/", views.students_list, name="list"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
]
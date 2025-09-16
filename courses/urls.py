from django.urls import path

from . import views

app_name = "courses"

urlpatterns = [
    path("list/", views.students_list, name="list"),
]

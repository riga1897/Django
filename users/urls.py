from django.urls import path

from users import views
from users.apps import UsersConfig

app_name = UsersConfig.name

urlpatterns = [
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.ProfileUpdateView.as_view(), name="profile_edit"),
]

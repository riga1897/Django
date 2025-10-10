from django.contrib.auth import views as auth_views
from django.urls import path

from apps.users import views

urlpatterns = [
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("verify-email/<str:token>/", views.EmailVerificationView.as_view(), name="email_verify"),
    path("email-verification-pending/", views.email_verification_pending, name="email_verification_pending"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.ProfileUpdateView.as_view(), name="profile_edit"),
    # Восстановление пароля
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(template_name="users/password_reset.html"),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="users/password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
        name="password_reset_complete",
    ),
    # Управление пользователями (для менеджеров)
    path("management/", views.UserManagementListView.as_view(), name="user_management_list"),
    path("management/<int:pk>/toggle-active/", views.UserToggleActiveView.as_view(), name="user_toggle_active"),
]

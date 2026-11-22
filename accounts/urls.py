from django.urls import path

from .views import ActivationView, LoginView, ProfileView, RegisterView

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("activation/", ActivationView.as_view(), name="activation"),
    path("register/", RegisterView.as_view(), name="register"),
]

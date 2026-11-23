from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import ActivationView, LoginView, PenaltiesHistoryView, ProfileView, RegisterView

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="accounts:login"), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("activation/", ActivationView.as_view(), name="activation"),
    path("register/", RegisterView.as_view(), name="register"),
]

conduct_urlpatterns = [
    path("conduta/", PenaltiesHistoryView.as_view(), name="history"),
]

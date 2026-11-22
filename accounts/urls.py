from django.urls import path

from .views import ActivationView, RegisterView

app_name = "accounts"

urlpatterns = [
    path("activation/", ActivationView.as_view(), name="activation"),
    path("register/", RegisterView.as_view(), name="register"),
]

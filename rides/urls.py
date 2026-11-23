from django.urls import path

from .views import MyOffersView, RideCreateView

app_name = "rides"
urlpatterns = [
    path("oferecer/", RideCreateView.as_view(), name="offer-create"),
    path("minhas-ofertas/", MyOffersView.as_view(), name="my-offers"),
]

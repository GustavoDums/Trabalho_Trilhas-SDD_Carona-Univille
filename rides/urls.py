from django.urls import path

from .views import MyOffersView, RideCreateView, RideSearchView

app_name = "rides"
urlpatterns = [
    path("buscar/", RideSearchView.as_view(), name="search"),
    path("oferecer/", RideCreateView.as_view(), name="offer-create"),
    path("minhas-ofertas/", MyOffersView.as_view(), name="my-offers"),
]

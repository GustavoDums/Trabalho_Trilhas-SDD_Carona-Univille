from django.urls import path

from .views import BookRideView, CancelBookingView, MyBookingsView, MyOffersView, RideCreateView, RideSearchView

app_name = "rides"
urlpatterns = [
    path("reservas/<int:booking_id>/cancelar/", CancelBookingView.as_view(), name="cancel_booking"),
    path("<int:offer_id>/reservar/", BookRideView.as_view(), name="book"),
    path("minhas-reservas/", MyBookingsView.as_view(), name="my_bookings"),
    path("buscar/", RideSearchView.as_view(), name="search"),
    path("oferecer/", RideCreateView.as_view(), name="offer-create"),
    path("minhas-ofertas/", MyOffersView.as_view(), name="my-offers"),
]

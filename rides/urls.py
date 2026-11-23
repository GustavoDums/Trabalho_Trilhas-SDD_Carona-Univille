from django.urls import path

from .views import (
    BookRideView, CancelBookingView, CancelOfferView, JoinWaitlistView, MyBookingsView, MyOffersView,
    RecurringOffersView, RemoveOfferView, RideCreateView, RideSearchView,
)

app_name = "rides"
urlpatterns = [
    path("<int:offer_id>/cancelar/", CancelOfferView.as_view(), name="cancel_offer"),
    path("<int:offer_id>/remover/", RemoveOfferView.as_view(), name="remove_offer"),
    path("reservas/<int:booking_id>/cancelar/", CancelBookingView.as_view(), name="cancel_booking"),
    path("<int:offer_id>/reservar/", BookRideView.as_view(), name="book"),
    path("<int:offer_id>/fila/", JoinWaitlistView.as_view(), name="join_waitlist"),
    path("minhas-reservas/", MyBookingsView.as_view(), name="my_bookings"),
    path("buscar/", RideSearchView.as_view(), name="search"),
    path("oferecer/", RideCreateView.as_view(), name="offer-create"),
    path("recorrentes/", RecurringOffersView.as_view(), name="recurring_offers"),
    path("minhas-ofertas/", MyOffersView.as_view(), name="my-offers"),
]

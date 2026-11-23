from django.urls import path
from .views import CompleteRideView, ReportNoShowView, SubmitReviewView

app_name = 'reviews'
urlpatterns = [
    path('caronas/<int:offer_id>/concluir/', CompleteRideView.as_view(), name='complete_ride'),
    path('reservas/<int:booking_id>/no-show/', ReportNoShowView.as_view(), name='report_no_show'),
    path('caronas/<int:offer_id>/usuarios/<int:reviewed_id>/nova/',
         SubmitReviewView.as_view(), name='submit_review'),
]

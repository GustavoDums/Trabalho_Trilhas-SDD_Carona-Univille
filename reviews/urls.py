from django.urls import path
from .views import SubmitReviewView

app_name = 'reviews'
urlpatterns = [
    path('caronas/<int:offer_id>/usuarios/<int:reviewed_id>/nova/',
         SubmitReviewView.as_view(), name='submit_review'),
]

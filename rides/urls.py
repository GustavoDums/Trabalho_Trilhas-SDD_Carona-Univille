from django.urls import path

from .views import RideCreateView

app_name = "rides"
urlpatterns = [path("oferecer/", RideCreateView.as_view(), name="offer-create")]

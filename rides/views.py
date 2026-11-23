from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.views.generic import TemplateView

from .forms import RideOfferForm, WaypointFormSet
from .models import RideOffer
from .services import publish_offer


class ActiveDriverRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "/accounts/login/"

    def test_func(self):
        user = self.request.user
        return user.is_active and user.role == "MOTORISTA" and user.is_activated


class RideCreateView(ActiveDriverRequiredMixin, TemplateView):
    template_name = "rides/offer_create.html"
    http_method_names = ["get", "post", "head", "options"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "form" not in context:
            vehicle = RideOffer.objects.filter(driver=self.request.user).order_by("-created_at", "-id").values(
                "vehicle_model", "vehicle_color", "vehicle_plate",
            ).first()
            context["form"] = RideOfferForm(initial=vehicle or {})
        context.setdefault("waypoint_formset", WaypointFormSet(prefix="waypoints"))
        return context

    def post(self, request, *args, **kwargs):
        form = RideOfferForm(request.POST)
        stops = WaypointFormSet(request.POST, prefix="waypoints")
        valid_offer, valid_stops = form.is_valid(), stops.is_valid()
        if valid_offer and valid_stops:
            try:
                publish_offer(driver=request.user, data=form.cleaned_data,
                              points=[entry.cleaned_data["point"] for entry in stops])
            except ValidationError as error:
                form.add_error(None, error)
            else:
                messages.success(request, "Oferta de carona publicada com sucesso.")
                return redirect("/caronas/minhas-ofertas/")
        # Mantém os demais dados para correção, sem reexibir a placa enviada.
        safe_data = form.data.copy()
        safe_data["vehicle_plate"] = ""
        form.data = safe_data
        return self.render_to_response(self.get_context_data(form=form, waypoint_formset=stops))

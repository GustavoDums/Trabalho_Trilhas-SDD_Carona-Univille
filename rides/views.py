from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import TemplateView
from django.views.generic import ListView
from django.db.models import Prefetch

from .forms import RecurringRideForm, RideBookingForm, RideOfferForm, RideSearchForm, WaypointFormSet
from .models import RECURRING_TIMEZONE, RecurringRideOccurrence, RecurringRideRule, RideOffer, Waypoint
from .services import publish_offer
from .services.booking_service import BookingService
from .services.booking_queries import BookingQueryService
from .services.cancellation_service import CancellationRefused, CancellationService
from .services.matching_service import MatchingService, SearchQuery
from .services.recurring_ride_service import HORIZON_DAYS, RecurringRideService


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


class MyOffersView(ActiveDriverRequiredMixin, ListView):
    """Feature 002/T005 local, roadmap T015 — consulta própria sem escrita."""

    template_name = "rides/my_offers.html"
    context_object_name = "offers"
    http_method_names = ["get", "head", "options"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["now"] = timezone.now()
        return context

    def get_queryset(self):
        return RideOffer.objects.filter(driver=self.request.user).select_related(
            "origin", "destination",
        ).prefetch_related(
            Prefetch("waypoints", queryset=Waypoint.objects.select_related("point").order_by("position")),
        ).order_by("departure_at", "created_at", "id")


class RecurringOffersView(ActiveDriverRequiredMixin, TemplateView):
    template_name = "rides/recurring_offers.html"
    http_method_names = ["get", "post", "head", "options"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        with timezone.override(RECURRING_TIMEZONE):
            today = timezone.localdate()
        window = RecurringRideOccurrence.objects.filter(
            local_date__range=(today, today + timedelta(days=HORIZON_DAYS - 1)),
        ).select_related("offer").only("rule_id", "local_date", "offer__status").order_by("local_date")
        context["rules"] = RecurringRideRule.objects.filter(driver=self.request.user).select_related(
            "origin", "destination",
        ).prefetch_related(Prefetch("occurrences", queryset=window, to_attr="upcoming")).order_by("-pk")
        context.setdefault("form", RecurringRideForm())
        context.setdefault("waypoint_formset", WaypointFormSet(prefix="waypoints"))
        return context

    def post(self, request, *args, **kwargs):
        form = RecurringRideForm(request.POST)
        stops = WaypointFormSet(request.POST, prefix="waypoints")
        valid_rule, valid_stops = form.is_valid(), stops.is_valid()
        if valid_rule and valid_stops:
            points = [stop.cleaned_data["point"] for stop in stops]
            route = [form.cleaned_data["origin"], *points, form.cleaned_data["destination"]]
            if len(route) != len(set(route)):
                form.add_error(None, "Origem, paradas e destino devem ser pontos distintos.")
            else:
                try:
                    result = RecurringRideService.create_rule(
                        driver=request.user, data=form.cleaned_data, points=points,
                    )
                except (ValidationError, IntegrityError):
                    form.add_error(None, "Não foi possível gerar as caronas. Confira os dados da regra.")
                else:
                    messages.success(request, f"Regra cadastrada. Caronas geradas: {len(result.created_dates)}.")
                    return redirect("rides:recurring_offers")
        form.data = form.data.copy()
        form.data["vehicle_plate"] = ""
        return self.render_to_response(self.get_context_data(form=form, waypoint_formset=stops), status=400)


class ActivePassengerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "/accounts/login/"

    def test_func(self):
        user = self.request.user
        return user.is_active and user.role == "PASSAGEIRO" and user.is_activated


class RideSearchView(ActivePassengerRequiredMixin, TemplateView):
    """Feature 003/T004 local — roadmap T019, consulta sem escrita."""

    template_name = "rides/search.html"
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        searched = bool(request.GET)
        form = RideSearchForm(request.GET if searched else None)
        results = ()
        if searched and form.is_valid():
            try:
                query = SearchQuery(
                    boarding_id=form.cleaned_data["boarding_id"].pk,
                    alighting_id=form.cleaned_data["alighting_id"].pk,
                    desired_at=form.cleaned_data["desired_at"],
                )
                results = MatchingService.search(passenger=request.user, query=query)
            except ValidationError as error:
                form.add_error(None, error)
        return self.render_to_response(self.get_context_data(
            form=form, searched=searched, results=results,
        ))


class ActiveAcademicRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = "/accounts/login/"

    def test_func(self):
        user = self.request.user
        return user.is_active and user.is_activated and user.role in ("MOTORISTA", "PASSAGEIRO")


class MyBookingsView(ActiveAcademicRequiredMixin, TemplateView):
    """Feature 004/T004 local — leitura própria, rotas na T005."""

    template_name = "rides/my_bookings.html"
    http_method_names = ["get"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bookings"] = BookingQueryService.list_for(user=self.request.user)
        return context


class BookRideView(ActivePassengerRequiredMixin, TemplateView):
    """Feature 004/T004 local — POST de reserva, sem registrar rota nesta tarefa."""

    template_name = "rides/my_bookings.html"
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        form = RideBookingForm(request.POST)
        if form.is_valid():
            try:
                BookingService.create_booking(
                    passenger=request.user, offer_id=kwargs["offer_id"],
                    boarding_point_id=form.cleaned_data["boarding_point_id"].pk,
                    alighting_point_id=form.cleaned_data["alighting_point_id"].pk,
                )
            except ValidationError as error:
                if hasattr(error, "error_dict"):
                    for field, errors in error.message_dict.items():
                        target = {"boarding_point": "boarding_point_id",
                                  "alighting_point": "alighting_point_id"}.get(field, field)
                        form.add_error(target if target in form.fields else None, errors)
                else:
                    form.add_error(None, error)
            else:
                messages.success(request, "Reserva confirmada com sucesso.")
                return redirect("/caronas/minhas-reservas/")
        return self.render_to_response(self.get_context_data(
            form=form, bookings=BookingQueryService.list_for(user=request.user),
        ))


class CancelBookingView(ActivePassengerRequiredMixin, TemplateView):
    """Feature 005/T005 local — POST do titular; política e locks no serviço."""

    template_name = "rides/my_bookings.html"
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        try:
            CancellationService.cancel_booking(user=request.user, booking_id=kwargs["booking_id"])
        except CancellationRefused:
            error = "Não é possível cancelar a partir do horário de saída da origem."
        except ValidationError:
            error = "Não foi possível cancelar a reserva."
        else:
            messages.success(request, "A reserva está cancelada.")
            return redirect("/caronas/minhas-reservas/")
        return self.render_to_response(self.get_context_data(
            cancellation_error=error,
            bookings=BookingQueryService.list_for(user=request.user),
        ), status=400)


class CancelOfferView(MyOffersView):
    """Feature 005/T006 local — cancela oferta própria via serviço atômico."""

    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        try:
            CancellationService.cancel_offer(user=request.user, offer_id=kwargs["offer_id"])
        except CancellationRefused:
            error = "Não é possível cancelar a partir do horário de saída da origem."
        except ValidationError:
            error = "Não foi possível cancelar a oferta."
        else:
            messages.success(request, "A oferta e suas reservas estão canceladas.")
            return redirect("/caronas/minhas-ofertas/")
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(
            cancellation_error=error,
        ), status=400)

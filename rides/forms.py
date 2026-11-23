"""Feature 002/T003 local — entrada de oferta e paradas ordenadas."""

from django import forms
from django.forms import BaseFormSet, formset_factory

from .models import RecurringRideRule, RideOffer, RoutePoint


class PointChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class RideOfferForm(forms.ModelForm):
    origin = PointChoiceField(queryset=RoutePoint.objects.all(), label="Origem")
    destination = PointChoiceField(queryset=RoutePoint.objects.all(), label="Destino")

    class Meta:
        model = RideOffer
        fields = ["origin", "destination", "departure_at", "seats", "vehicle_model", "vehicle_color", "vehicle_plate"]
        labels = {"departure_at": "Saída (America/Sao_Paulo)", "seats": "Vagas para passageiros",
                  "vehicle_model": "Modelo do veículo", "vehicle_color": "Cor", "vehicle_plate": "Placa"}
        widgets = {"departure_at": forms.DateTimeInput(format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"})}


class RecurringRideForm(RideOfferForm):
    weekdays = forms.TypedMultipleChoiceField(
        label="Dias da semana", coerce=int, widget=forms.CheckboxSelectMultiple,
        choices=enumerate(("Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
                           "Sexta-feira", "Sábado", "Domingo")),
    )

    class Meta(RideOfferForm.Meta):
        model = RecurringRideRule
        fields = ["origin", "destination", "weekdays", "local_time", "seats",
                  "vehicle_model", "vehicle_color", "vehicle_plate"]
        labels = {**RideOfferForm.Meta.labels, "local_time": "Horário de saída (America/Sao_Paulo)"}
        widgets = {"local_time": forms.TimeInput(format="%H:%M", attrs={"type": "time"})}


class WaypointForm(forms.Form):
    point = PointChoiceField(queryset=RoutePoint.objects.all(), label="Parada intermediária")


class RequiredWaypointFormSet(BaseFormSet):
    def _construct_form(self, i, **kwargs):
        form = super()._construct_form(i, **kwargs)
        form.empty_permitted = False
        return form

    def clean(self):
        super().clean()
        if not self.management_form.is_valid():
            return
        management = self.management_form.cleaned_data
        if management["TOTAL_FORMS"] < 0 or management["INITIAL_FORMS"] != 0:
            raise forms.ValidationError("Dados de controle das paradas inválidos. Confira as paradas e envie novamente.")


WaypointFormSet = formset_factory(WaypointForm, formset=RequiredWaypointFormSet, extra=0)


class SearchDateTimeField(forms.DateTimeField):
    """Entrada local de Joinville, independente do fuso ativo do request."""

    def to_python(self, value):
        from django.utils import timezone

        with timezone.override("America/Sao_Paulo"):
            return super().to_python(value)


class RideSearchForm(forms.Form):
    boarding_id = PointChoiceField(queryset=RoutePoint.objects.all(), label="Embarque")
    alighting_id = PointChoiceField(queryset=RoutePoint.objects.all(), label="Desembarque")
    desired_at = SearchDateTimeField(
        label="Data e horário desejado (America/Sao_Paulo)",
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M:%S", attrs={"type": "datetime-local", "step": "1"}),
        help_text="Janela fixa de ±30 minutos em relação à saída da origem.",
    )

    def clean(self):
        cleaned = super().clean()
        boarding = cleaned.get("boarding_id")
        alighting = cleaned.get("alighting_id")
        if boarding is not None and alighting is not None and boarding.pk == alighting.pk:
            self.add_error("alighting_id", "Embarque e desembarque devem ser distintos.")
        return cleaned


class RideBookingForm(forms.Form):
    boarding_point_id = PointChoiceField(queryset=RoutePoint.objects.all(), label="Embarque")
    alighting_point_id = PointChoiceField(queryset=RoutePoint.objects.all(), label="Desembarque")

    def clean(self):
        cleaned = super().clean()
        boarding = cleaned.get("boarding_point_id")
        alighting = cleaned.get("alighting_point_id")
        if boarding is not None and alighting is not None and boarding.pk == alighting.pk:
            self.add_error("alighting_point_id", "Embarque e desembarque devem ser distintos.")
        return cleaned

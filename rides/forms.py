"""Feature 002/T003 local — entrada de oferta e paradas ordenadas."""

from django import forms
from django.forms import BaseFormSet, formset_factory

from .models import RideOffer, RoutePoint


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

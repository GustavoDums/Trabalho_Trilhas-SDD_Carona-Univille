"""Entrada do operador para completar a janela das regras recorrentes."""
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError
from django.utils import timezone

from rides.models import RecurringRideRule
from rides.services.recurring_ride_service import RecurringRideService


def format_dates(dates):
    return ",".join(day.isoformat() for day in dates) or "-"


class Command(BaseCommand):
    help = "Gera as caronas futuras de uma regra ou de todas as regras ativas."

    def add_arguments(self, parser):
        selection = parser.add_mutually_exclusive_group(required=True)
        selection.add_argument("--rule", type=int, metavar="ID", help="Identificador de uma regra.")
        selection.add_argument("--all", action="store_true", help="Seleciona todas as regras ativas.")

    def handle(self, *, rule, **options):
        rules = RecurringRideRule.objects.select_related("driver").order_by("pk")
        if rule is None:
            selection = rules.filter(active=True).iterator()
        else:
            if rule <= 0:
                raise CommandError("Informe um identificador positivo para --rule.")
            try:
                selection = (rules.get(pk=rule),)
            except RecurringRideRule.DoesNotExist:
                raise CommandError("Regra recorrente inexistente.") from None

        reference = timezone.now()
        failed = False
        for item in selection:
            try:
                result = RecurringRideService.generate(
                    rule_id=item.pk, driver=item.driver, clock=lambda: reference,
                )
            except PermissionDenied:
                self.stdout.write(f"regra={item.pk} ignorada por inelegibilidade")
            except (ValidationError, DatabaseError):
                failed = True
                self.stderr.write(f"regra={item.pk} falhou")
            else:
                self.stdout.write(
                    f"regra={item.pk} criadas={format_dates(result.created_dates)} "
                    f"existentes={format_dates(result.existing_dates)}",
                )
        if failed:
            raise CommandError("Falha na geração de uma ou mais regras recorrentes.")

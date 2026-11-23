"""Avaliação, conclusão e denúncia com validação no servidor."""
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.views.generic import TemplateView, View

from rides.views import ActiveAcademicRequiredMixin, ActiveDriverRequiredMixin
from .forms import RideReviewForm
from .services.penalty_service import PenaltyService
from .services.review_service import ReviewService


class SubmitReviewView(ActiveAcademicRequiredMixin, TemplateView):
    template_name = 'reviews/submit_review.html'
    http_method_names = ['get', 'post']

    def _review_context(self):
        return ReviewService.review_context(
            user=self.request.user, offer_id=self.kwargs['offer_id'],
            reviewed_user_id=self.kwargs['reviewed_id'],
        )

    def _unavailable(self):
        return self.render_to_response(self.get_context_data(
            review_error='Não foi possível disponibilizar ou registrar esta avaliação.',
        ), status=400)

    def get(self, request, *args, **kwargs):
        try:
            context = self._review_context()
        except ValidationError:
            return self._unavailable()
        return self.render_to_response(self.get_context_data(
            form=RideReviewForm(), review_context=context,
        ))

    def post(self, request, *args, **kwargs):
        try:
            context = self._review_context()
        except ValidationError:
            return self._unavailable()
        form = RideReviewForm(request.POST)
        if form.is_valid():
            try:
                ReviewService.create_review(
                    user=request.user, offer_id=kwargs['offer_id'],
                    reviewed_user_id=kwargs['reviewed_id'], **form.cleaned_data,
                )
            except ValidationError:
                return self._unavailable()
            messages.success(request, 'Avaliação registrada com sucesso.')
            return redirect('/accounts/profile/')
        return self.render_to_response(self.get_context_data(
            form=form, review_context=context,
        ), status=400)


class CompleteRideView(ActiveDriverRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, *, offer_id):
        try:
            ReviewService.complete_offer(user=request.user, offer_id=offer_id)
        except ValidationError as error:
            return HttpResponseBadRequest(error.messages[0], content_type='text/plain; charset=utf-8')
        messages.success(request, 'Conclusão da carona registrada.')
        return redirect('rides:my-offers')


class ReportNoShowView(ActiveAcademicRequiredMixin, TemplateView):
    template_name = 'reviews/report_no_show.html'
    http_method_names = ['get', 'post']

    def _unavailable(self, error):
        return self.render_to_response(self.get_context_data(report_error=error.messages[0]), status=400)

    def get(self, request, *, booking_id):
        try:
            context = PenaltyService.no_show_context(user=request.user, booking_id=booking_id)
        except ValidationError as error:
            return self._unavailable(error)
        return self.render_to_response(self.get_context_data(report_context=context))

    def post(self, request, *, booking_id):
        try:
            PenaltyService.report_no_show(
                user=request.user, booking_id=booking_id, declared=request.POST.get('declared') == 'yes',
            )
        except ValidationError as error:
            return self._unavailable(error)
        messages.success(request, 'Declaração de ausência registrada.')
        return redirect('rides:my_bookings')

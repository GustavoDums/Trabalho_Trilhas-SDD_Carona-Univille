"""Feature 006/T004 unificada — formulário autorizado, revalidação no POST."""
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.views.generic import TemplateView

from rides.views import ActiveAcademicRequiredMixin
from .forms import RideReviewForm
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

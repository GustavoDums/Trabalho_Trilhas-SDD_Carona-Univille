"""Feature 006/T004 unificada — somente dados editáveis da avaliação."""
from django import forms


class RideReviewForm(forms.Form):
    rating = forms.IntegerField(label='Nota', min_value=1, max_value=5,
                                help_text='Escolha uma nota inteira de 1 a 5.')
    comment = forms.CharField(label='Comentário (opcional)', max_length=500, required=False,
                              widget=forms.Textarea(attrs={'rows': 4}),
                              help_text='Até 500 caracteres. Evite incluir dados pessoais.')

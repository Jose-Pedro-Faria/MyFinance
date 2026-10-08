from django import forms
from .models import Investimento


class InvestimentoForm(forms.ModelForm):
    class Meta:
        model = Investimento
        fields = ["categoria", "nome", "unidades", "valor_unitario", "corretora"]
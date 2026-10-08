from django import forms
from .models import Divida


class DividaForm(forms.ModelForm):
    class Meta:
        model = Divida
        fields = [
            "entidade", "loja", "item",
            "mensalidade", "meses_em_falta", "dia_pagamento",
        ]
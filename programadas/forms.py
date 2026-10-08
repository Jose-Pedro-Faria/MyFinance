from decimal import InvalidOperation

from django import forms

from config.calculos import calcular
from .models import DespesaProgramada


class DespesaForm(forms.ModelForm):
    valor = forms.CharField(
        label="Valor (€)",
        help_text="Podes escrever somas, por exemplo 50+20+100",
    )

    class Meta:
        model = DespesaProgramada
        fields = ["data", "descricao", "valor"]
        widgets = {
            "data": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial["valor"] = self.instance.expressao or self.instance.valor

    def clean_valor(self):
        try:
            return calcular(self.cleaned_data["valor"])
        except (ValueError, SyntaxError, InvalidOperation, ZeroDivisionError):
            raise forms.ValidationError(
                "Valor inválido. Usa números e as operações + - * / (ex.: 50+20+100)."
            )

    def save(self, commit=True):
        despesa = super().save(commit=False)
        despesa.expressao = self.data.get(self.add_prefix("valor"), "").strip()
        if commit:
            despesa.save()
        return despesa
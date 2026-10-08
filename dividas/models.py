from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Divida(models.Model):
    entidade = models.CharField("Entidade de crédito", max_length=100)
    loja = models.CharField("Loja", max_length=100, blank=True)
    item = models.CharField("Item creditado", max_length=150)
    mensalidade = models.DecimalField("Mensalidade (€)", max_digits=10, decimal_places=2)
    meses_em_falta = models.PositiveIntegerField("Meses em falta")
    dia_pagamento = models.PositiveSmallIntegerField(
        "Dia acordado para pagamento",
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        help_text="Dia do mês (1 a 31)",
    )

    class Meta:
        ordering = ["dia_pagamento", "entidade"]

    @property
    def total_em_falta(self):
        return self.mensalidade * self.meses_em_falta

    def __str__(self):
        return f"{self.entidade} - {self.item}"
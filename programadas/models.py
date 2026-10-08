from django.db import models


class DespesaProgramada(models.Model):
    data = models.DateField("Data")
    descricao = models.CharField("Despesa", max_length=150)
    valor = models.DecimalField("Valor (€)", max_digits=12, decimal_places=2)
    expressao = models.CharField(max_length=200, blank=True, default="")
    paga = models.BooleanField("Paga", default=False)

    class Meta:
        ordering = ["data", "descricao"]

    def __str__(self):
        return f"{self.data:%d/%m/%Y} - {self.descricao}"
from django.db import models


class SubCategoria(models.Model):
    class Tipo(models.TextChoices):
        RECEITA = "REC", "Receita"
        ESSENCIAL = "ESS", "Despesas Essenciais"
        NAO_ESSENCIAL = "NES", "Despesas Não Essenciais"
        INVESTIMENTO = "INV", "Investimento"

    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=3, choices=Tipo.choices)
    ativa = models.BooleanField(default=True)

    class Meta:
        ordering = ["tipo", "nome"]

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"


class Relatorio(models.Model):
    mes = models.DateField(unique=True, help_text="Usa sempre o dia 1 do mês")

    class Meta:
        ordering = ["-mes"]

    def __str__(self):
        return self.mes.strftime("%m/%Y")


class Lancamento(models.Model):
    relatorio = models.ForeignKey(
        Relatorio, on_delete=models.CASCADE, related_name="lancamentos"
    )
    subcategoria = models.ForeignKey(SubCategoria, on_delete=models.PROTECT)
    montante = models.DecimalField(max_digits=12, decimal_places=2)
    expressao = models.CharField(max_length=200, blank=True, default="")

    class Meta:
        unique_together = ("relatorio", "subcategoria")

    def __str__(self):
        return f"{self.relatorio} - {self.subcategoria.nome}: {self.montante}"
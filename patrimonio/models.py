from django.db import models


class Categoria(models.Model):
    class Grupo(models.TextChoices):
        DINHEIRO = "DIN", "Dinheiro"
        EMERGENCIA = "EME", "Emergência"
        INVESTIMENTOS = "INV", "Investimentos"

    nome = models.CharField(max_length=100)
    grupo = models.CharField(max_length=3, choices=Grupo.choices)
    ativa = models.BooleanField(default=True)

    class Meta:
        ordering = ["grupo", "nome"]

    def __str__(self):
        return f"{self.nome} ({self.get_grupo_display()})"


class RegistoMensal(models.Model):
    mes = models.DateField(unique=True, help_text="Usa sempre o dia 1 do mês")

    class Meta:
        ordering = ["-mes"]

    def __str__(self):
        return self.mes.strftime("%m/%Y")


class Valor(models.Model):
    registo = models.ForeignKey(
        RegistoMensal, on_delete=models.CASCADE, related_name="valores"
    )
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    montante = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ("registo", "categoria")

    def __str__(self):
        return f"{self.registo} - {self.categoria.nome}: {self.montante}"
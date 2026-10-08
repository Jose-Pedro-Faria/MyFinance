from django.db import models


class Categoria(models.TextChoices):
    ACOES_NACIONAIS = "AN", "Ações Nacionais"
    ACOES_MUNDIAIS = "AM", "Ações Mundiais"
    CRIPTO = "CR", "Cripto"
    COMMODITIES = "CO", "Commodities"
    CAIXA = "CX", "Caixa"


class Posicao(models.Model):
    """Campos comuns às posições atuais e às cópias guardadas nas capturas."""

    categoria = models.CharField("Categoria", max_length=2, choices=Categoria.choices)
    nome = models.CharField("Nome", max_length=100)
    unidades = models.DecimalField("Unidades", max_digits=18, decimal_places=8)
    valor_unitario = models.DecimalField(
        "Valor unitário (€)", max_digits=14, decimal_places=4
    )
    corretora = models.CharField("Corretora", max_length=100, blank=True)

    class Meta:
        abstract = True
        ordering = ["categoria", "nome"]

    @property
    def valor_total(self):
        return self.unidades * self.valor_unitario


class Investimento(Posicao):
    """Posição atual. É isto que as contas e a Home usam."""

    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} ({self.get_categoria_display()})"


class Captura(models.Model):
    """Fotografia de todas as posições num determinado momento."""

    data = models.DateTimeField(auto_now_add=True)
    nota = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-data"]

    def __str__(self):
        return f"Captura {self.data:%d/%m/%Y %H:%M}"


class CapturaItem(Posicao):
    captura = models.ForeignKey(Captura, on_delete=models.CASCADE, related_name="itens")

    def __str__(self):
        return f"{self.captura} - {self.nome}"
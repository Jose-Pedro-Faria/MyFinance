from datetime import date

MESES = [
    (1, "Janeiro"), (2, "Fevereiro"), (3, "Março"), (4, "Abril"),
    (5, "Maio"), (6, "Junho"), (7, "Julho"), (8, "Agosto"),
    (9, "Setembro"), (10, "Outubro"), (11, "Novembro"), (12, "Dezembro"),
]


def anos_disponiveis():
    """Do próximo ano até 15 anos atrás, do mais recente para o mais antigo."""
    atual = date.today().year
    return list(range(atual + 1, atual - 15, -1))


def ler_mes(request):
    """Lê 'ano' e 'mes' do formulário e devolve a data (dia 1), ou None se inválido."""
    try:
        return date(int(request.POST["ano"]), int(request.POST["mes"]), 1)
    except (KeyError, ValueError):
        return None
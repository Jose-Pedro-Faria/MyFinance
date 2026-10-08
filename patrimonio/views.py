from datetime import date
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from config.calculos import calcular
from config.datas import MESES, anos_disponiveis, ler_mes

from .forms import CategoriaForm
from .models import Categoria, RegistoMensal, Valor

GRUPOS = [("DIN", "Dinheiro"), ("EME", "Emergência"), ("INV", "Investimentos")]


def lista(request):
    categorias = Categoria.objects.all()
    grupos = [
        {
            "cod": cod,
            "nome": nome,
            "categorias": [c for c in categorias if c.grupo == cod],
        }
        for cod, nome in GRUPOS
    ]

    linhas = []
    for r in RegistoMensal.objects.prefetch_related("valores"):
        por_categoria = {v.categoria_id: v.montante for v in r.valores.all()}
        celulas = []
        total = Decimal("0")
        emergencia = Decimal("0")
        for g in grupos:
            valores = [por_categoria.get(c.id) for c in g["categorias"]]
            soma = sum((v for v in valores if v is not None), Decimal("0"))
            celulas.append({"cod": g["cod"], "total": soma, "valores": valores})
            total += soma
            if g["cod"] == "EME":
                emergencia = soma
        linhas.append({
            "pk": r.pk,
            "mes": r.mes,
            "grupos": celulas,
            "total": total,
            "sem_emergencia": total - emergencia,
        })

    return render(request, "patrimonio/lista.html", {"grupos": grupos, "linhas": linhas})


# ---------- Funções de apoio ao formulário ----------

def _ler_digitado(request, categorias):
    return {c.id: request.POST.get(f"cat_{c.id}", "").strip() for c in categorias}


def _calcular_valores(categorias, digitado):
    try:
        return {
            c: (calcular(digitado[c.id]), digitado[c.id])
            for c in categorias if digitado[c.id]
        }
    except (ValueError, SyntaxError, InvalidOperation, ZeroDivisionError):
        raise ValueError("Há um valor inválido. Usa números e as operações + - * / (ex.: 1200+350).")


def _guardar_valores(registo, categorias, valores, digitado):
    for c, (montante, expressao) in valores.items():
        Valor.objects.update_or_create(
            registo=registo, categoria=c,
            defaults={"montante": montante, "expressao": expressao},
        )
    vazias = [c for c in categorias if not digitado[c.id]]
    Valor.objects.filter(registo=registo, categoria__in=vazias).delete()


# ---------- Novo / editar / apagar ----------

def novo_registo(request):
    categorias = list(Categoria.objects.filter(ativa=True))
    existentes = [m.strftime("%Y-%m") for m in RegistoMensal.objects.values_list("mes", flat=True)]
    hoje = date.today()
    ano_sel, mes_sel = hoje.year, hoje.month
    digitado = {}
    erro = None

    if request.method == "POST":
        digitado = _ler_digitado(request, categorias)
        data = ler_mes(request)
        if data is None:
            erro = "Escolhe um mês e um ano válidos."
        else:
            ano_sel, mes_sel = data.year, data.month
            if RegistoMensal.objects.filter(mes=data).exists():
                erro = "Já existe um registo para este mês. Vai à tabela e carrega em Editar."
            else:
                try:
                    valores = _calcular_valores(categorias, digitado)
                except ValueError as e:
                    erro = str(e)
                else:
                    with transaction.atomic():
                        registo = RegistoMensal.objects.create(mes=data)
                        _guardar_valores(registo, categorias, valores, digitado)
                    return redirect("patrimonio:lista")

    for c in categorias:
        c.valor_atual = digitado.get(c.id, "")

    return render(request, "patrimonio/novo.html", {
        "categorias": categorias,
        "erro": erro,
        "meses": MESES,
        "anos": anos_disponiveis(),
        "ano_sel": ano_sel,
        "mes_sel": mes_sel,
        "existentes": existentes,
    })


def editar_registo(request, pk):
    registo = get_object_or_404(RegistoMensal, pk=pk)
    categorias = list(Categoria.objects.filter(ativa=True))
    erro = None

    if request.method == "POST":
        digitado = _ler_digitado(request, categorias)
        try:
            valores = _calcular_valores(categorias, digitado)
        except ValueError as e:
            erro = str(e)
        else:
            with transaction.atomic():
                _guardar_valores(registo, categorias, valores, digitado)
            return redirect("patrimonio:lista")
    else:
        atuais = Valor.objects.filter(registo=registo)
        digitado = {v.categoria_id: (v.expressao or str(v.montante)) for v in atuais}

    for c in categorias:
        c.valor_atual = digitado.get(c.id, "")

    return render(request, "patrimonio/editar.html", {
        "registo": registo,
        "categorias": categorias,
        "erro": erro,
    })


@require_POST
def apagar_registo(request, pk):
    get_object_or_404(RegistoMensal, pk=pk).delete()
    return redirect("patrimonio:lista")


def nova_categoria(request):
    form = CategoriaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("patrimonio:novo")
    return render(request, "patrimonio/categoria.html", {"form": form})
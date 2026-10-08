from datetime import date
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.shortcuts import redirect, render

from .forms import CategoriaForm
from .models import Categoria, RegistoMensal, Valor

from config.calculos import calcular


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
            "mes": r.mes,
            "grupos": celulas,
            "total": total,
            "sem_emergencia": total - emergencia,
        })

    return render(request, "patrimonio/lista.html", {"grupos": grupos, "linhas": linhas})


def novo_registo(request):
    categorias = list(Categoria.objects.filter(ativa=True))
    erro = None

    mes_txt = request.POST.get("mes") or request.GET.get("mes") or date.today().strftime("%Y-%m")
    try:
        ano, mes = mes_txt.split("-")
        data = date(int(ano), int(mes), 1)
    except ValueError:
        data = date.today().replace(day=1)
        mes_txt = data.strftime("%Y-%m")

    if request.method == "POST":
        digitado = {c.id: request.POST.get(f"cat_{c.id}", "").strip() for c in categorias}
        try:
            valores = {
                c: (calcular(digitado[c.id]), digitado[c.id])
                for c in categorias if digitado[c.id]
            }
        except (ValueError, SyntaxError, InvalidOperation, ZeroDivisionError):
            erro = "Há um valor inválido. Usa números e as operações + - * / (ex.: 1200+350)."
        else:
            with transaction.atomic():
                registo, _ = RegistoMensal.objects.get_or_create(mes=data)
                for c, (montante, expressao) in valores.items():
                    Valor.objects.update_or_create(
                        registo=registo, categoria=c,
                        defaults={"montante": montante, "expressao": expressao},
                    )
                vazias = [c for c in categorias if not digitado[c.id]]
                Valor.objects.filter(registo=registo, categoria__in=vazias).delete()
            return redirect("patrimonio:lista")
    else:
        existentes = Valor.objects.filter(registo__mes=data)
        digitado = {v.categoria_id: (v.expressao or str(v.montante)) for v in existentes}

    for c in categorias:
        c.valor_atual = digitado.get(c.id, "")

    return render(request, "patrimonio/novo.html", {
        "categorias": categorias,
        "erro": erro,
        "mes_txt": mes_txt,
    })


def nova_categoria(request):
    form = CategoriaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("patrimonio:novo")
    return render(request, "patrimonio/categoria.html", {"form": form})
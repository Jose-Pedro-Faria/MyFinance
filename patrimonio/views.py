from datetime import date
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.shortcuts import redirect, render

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
            "mes": r.mes,
            "grupos": celulas,
            "total": total,
            "sem_emergencia": total - emergencia,
        })

    return render(request, "patrimonio/lista.html", {"grupos": grupos, "linhas": linhas})


def novo_registo(request):
    categorias = Categoria.objects.filter(ativa=True)
    erro = None

    if request.method == "POST":
        try:
            ano, mes = request.POST["mes"].split("-")
            data = date(int(ano), int(mes), 1)
            valores = {}
            for c in categorias:
                bruto = request.POST.get(f"cat_{c.id}", "").strip().replace(",", ".")
                if bruto:
                    valores[c] = Decimal(bruto)
        except (ValueError, InvalidOperation, KeyError):
            erro = "Verifica o mês e os valores introduzidos."
        else:
            with transaction.atomic():
                registo, _ = RegistoMensal.objects.get_or_create(mes=data)
                for c, montante in valores.items():
                    Valor.objects.update_or_create(
                        registo=registo, categoria=c,
                        defaults={"montante": montante},
                    )
            return redirect("patrimonio:lista")

    return render(request, "patrimonio/novo.html", {
        "categorias": categorias,
        "erro": erro,
        "hoje": date.today(),
    })


def nova_categoria(request):
    form = CategoriaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("patrimonio:novo")
    return render(request, "patrimonio/categoria.html", {"form": form})
import shutil
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Cria uma cópia de segurança consistente da base de dados SQLite."

    def add_arguments(self, parser):
        parser.add_argument(
            "--destino", default=str(settings.BASE_DIR / "backups"),
            help="Pasta onde guardar as cópias",
        )
        parser.add_argument(
            "--manter", type=int, default=30,
            help="Número de cópias a manter (as mais antigas são apagadas)",
        )

    def handle(self, *args, **opcoes):
        db = settings.DATABASES["default"]
        if "sqlite3" not in db["ENGINE"]:
            raise CommandError("Este comando só suporta SQLite.")

        destino = Path(opcoes["destino"])
        destino.mkdir(parents=True, exist_ok=True)
        nome = f"db-{datetime.now():%Y%m%d-%H%M%S}.sqlite3"

        with tempfile.TemporaryDirectory() as tmp:
            temporario = Path(tmp) / nome
            origem = sqlite3.connect(db["NAME"])
            copia = sqlite3.connect(temporario)
            origem.backup(copia)
            copia.close()
            origem.close()
            ficheiro = destino / nome
            shutil.copy2(temporario, ficheiro)

        manter = max(opcoes["manter"], 1)
        antigas = sorted(destino.glob("db-*.sqlite3"))[:-manter]
        for f in antigas:
            f.unlink()

        self.stdout.write(self.style.SUCCESS(f"Cópia criada: {ficheiro}"))
        if antigas:
            self.stdout.write(f"{len(antigas)} cópia(s) antiga(s) apagada(s).")
#!/usr/bin/env python3
"""Arma los dos HTML que se abren con doble clic, a partir de app.html.

  megafonia.html        equipo de ejemplo, es el que va al repo público
  megafonia-local.html  con el equipo real, queda fuera de git

app.html no sirve para abrir directo: no lleva <html>/<head>/<body> porque el
visor de artifacts se los pone. Un navegador que abre ese archivo se queda
parseando dentro de <head> y la página sale en blanco. Acá se envuelve en un
documento completo, con doctype, para que funcione con doble clic.

    python3 hacer-plantilla.py
"""

import io
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
ORIGEN = BASE / "app.html"
DESTINO = BASE / "megafonia.html"
LOCAL = BASE / "megafonia-local.html"
PATRON = r'(<script type="application/json" id="estado">\n?)(.*?)(\n?</script>)'

EJEMPLO = {
    "equipo": [
        {"id": "ana",    "nombre": "Ana Ejemplo",     "puestos": ["camara", "audio", "produccion", "streaming", "tarde"], "activo": True},
        {"id": "bruno",  "nombre": "Bruno Ejemplo",   "puestos": ["camara", "produccion", "streaming", "tarde"],          "activo": True},
        {"id": "carla",  "nombre": "Carla Ejemplo",   "puestos": ["audio"],                                               "activo": True},
        {"id": "diego",  "nombre": "Diego Ejemplo",   "puestos": ["produccion", "streaming"],                             "activo": True},
        {"id": "elena",  "nombre": "Elena Ejemplo",   "puestos": ["camara", "audio", "produccion", "streaming", "tarde"], "activo": True},
        {"id": "fabian", "nombre": "Fabián Ejemplo",  "puestos": ["produccion", "streaming", "tarde"],                    "activo": True},
        {"id": "gabi",   "nombre": "Gabi Ejemplo",    "puestos": ["camara", "audio", "tarde"],                            "activo": True},
    ],
    "config": {"dias": [6], "tardeExclusiva": True},
    "plannings": {},
    "mesActual": None,
}


def envolver(fragmento):
    """app.html es un fragmento; acá se convierte en un documento HTML válido."""
    corte = fragmento.index('<script type="application/json"')
    cabeza, cuerpo = fragmento[:corte].rstrip(), fragmento[corte:].strip()
    return ('<!doctype html>\n<html lang="es">\n<head>\n'
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            + cabeza + '\n</head>\n<body>\n' + cuerpo + '\n</body>\n</html>\n')


def main():
    if not ORIGEN.exists():
        sys.exit(f"No encuentro {ORIGEN.name}.")
    fuente = io.open(ORIGEN, encoding="utf-8").read()
    if not re.search(PATRON, fuente, re.S):
        sys.exit("No encuentro el bloque de estado en app.html.")

    datos = json.dumps(EJEMPLO, ensure_ascii=False, indent=2)
    salida = re.sub(PATRON, lambda m: m.group(1) + datos + m.group(3), fuente, count=1, flags=re.S)

    # Red de seguridad: ningún nombre real puede quedar en lo que se publica.
    reales = [p["nombre"] for p in json.loads(re.search(PATRON, fuente, re.S).group(2))["equipo"]]
    filtrados = [n for n in reales if n and n in salida]
    if filtrados:
        sys.exit("ABORTADO: estos nombres siguen apareciendo en la plantilla: " + ", ".join(filtrados))

    io.open(DESTINO, "w", encoding="utf-8").write(envolver(salida))
    print(f"{DESTINO.name} generado — equipo de ejemplo ({len(EJEMPLO['equipo'])} personas), "
          f"sin plannings.")
    print(f"  verificado: ninguno de los {len(reales)} nombres reales aparece en el archivo.")

    io.open(LOCAL, "w", encoding="utf-8").write(envolver(fuente))
    print(f"{LOCAL.name} generado — con tu equipo real, excluido de git.")
    print("  este es el que se abre con doble clic desde el Escritorio.")


if __name__ == "__main__":
    main()

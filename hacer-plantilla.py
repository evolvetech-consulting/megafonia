#!/usr/bin/env python3
"""Genera megafonia.html: la app con un equipo de ejemplo, sin los datos reales.

app.html lleva adentro el equipo y los plannings de la iglesia, así que no se
publica. Esta plantilla tiene el mismo código y un equipo inventado; los datos
de verdad viven en el enlace privado y en el navegador de cada uno.

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

    io.open(DESTINO, "w", encoding="utf-8").write(salida)
    print(f"{DESTINO.name} generado ({len(salida)} bytes)")
    print(f"Equipo de ejemplo: {len(EJEMPLO['equipo'])} personas, sin plannings.")
    print(f"Verificado: ninguno de los {len(reales)} nombres reales aparece en el archivo.")


if __name__ == "__main__":
    main()

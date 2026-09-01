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
    "equipoActual": "equipo-1",
    "mesActual": None,
    "equipos": [{
        "id": "equipo-1",
        "nombre": "Megafonía",
        "puestos": [
            {"id": "camara",     "label": "Cámara",     "emoji": "🎥", "cupo": 1, "color": "#8B6BC7"},
            {"id": "audio",      "label": "Audio",      "emoji": "🎙️", "cupo": 1, "color": "#D97B2E"},
            {"id": "produccion", "label": "Producción", "emoji": "🎛️", "cupo": 1, "color": "#34A07A"},
            {"id": "streaming",  "label": "Streaming",  "emoji": "📡", "cupo": 1, "color": "#C75577"},
            {"id": "tarde",      "label": "Tarde",      "emoji": "🌇", "cupo": 2, "color": "#4A87C4",
             "otroTurno": True},
        ],
        "gente": [
            {"id": "ana",    "nombre": "Ana Ejemplo",    "puestos": ["camara","audio","produccion","streaming","tarde"], "activo": True},
            {"id": "bruno",  "nombre": "Bruno Ejemplo",  "puestos": ["camara","produccion","streaming","tarde"],          "activo": True},
            {"id": "carla",  "nombre": "Carla Ejemplo",  "puestos": ["audio"],                                            "activo": True},
            {"id": "diego",  "nombre": "Diego Ejemplo",  "puestos": ["produccion","streaming"],                           "activo": True},
            {"id": "elena",  "nombre": "Elena Ejemplo",  "puestos": ["camara","audio","produccion","streaming","tarde"], "activo": True},
            {"id": "fabian", "nombre": "Fabián Ejemplo", "puestos": ["produccion","streaming","tarde"],                    "activo": True},
            {"id": "gabi",   "nombre": "Gabi Ejemplo",   "puestos": ["camara","audio","tarde"],                            "activo": True},
        ],
        "config": {"dias": [6], "tardeExclusiva": True},
        "plannings": {}, "notas": {}, "restricciones": {}, "enviados": {},
    }],
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

    # Red de seguridad: ni el nombre completo ni sus partes sueltas. Una vez se
    # coló un nombre de pila en un texto de ejemplo porque solo se buscaba el nombre
    # entero; desde entonces se revisa también cada palabra por separado.
    crudo = json.loads(re.search(PATRON, fuente, re.S).group(2))
    equipos = crudo.get("equipos") or [{"gente": crudo.get("equipo", [])}]
    personas = [p for t in equipos for p in t.get("gente", [])]
    reales = [p.get("nombre", "") for p in personas]

    # Teléfonos y correos: más sensibles que los nombres, y basta un dígito
    # distinto para que un filtro por nombre no los vea.
    contactos = set()
    for p in personas:
        for campo in ("tel", "email"):
            v = str(p.get(campo) or "").strip()
            if v:
                contactos.add(v)
                if campo == "tel":
                    contactos.add(re.sub(r"\D", "", v))
    colados = sorted(c for c in contactos if c and c in salida)
    if colados:
        sys.exit("ABORTADO: datos de contacto en la plantilla: " + ", ".join(colados))

    # Y por las dudas, que no quede ningún correo ni teléfono largo suelto.
    sueltos = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", salida)
    sueltos = [x for x in sueltos if not x.endswith(("ejemplo.com", "@ejemplo"))]
    if sueltos:
        sys.exit("ABORTADO: correos en la plantilla: " + ", ".join(sorted(set(sueltos))))
    piezas = set()
    for nombre in reales:
        if not nombre:
            continue
        piezas.add(nombre)
        for parte in nombre.split():
            if len(parte) > 3 and parte.lower() not in ("de", "del", "la", "las", "los"):
                piezas.add(parte)
    # Palabras completas: "Ilia" no debe saltar por la palabra "familia".
    filtrados = sorted(p for p in piezas
                       if re.search(r"(?<![\w])" + re.escape(p) + r"(?![\w])", salida, re.I))
    if filtrados:
        sys.exit("ABORTADO: esto sigue apareciendo en la plantilla: " + ", ".join(filtrados))

    io.open(DESTINO, "w", encoding="utf-8").write(envolver(salida))
    print(f"{DESTINO.name} generado — equipo de ejemplo ({len(EJEMPLO['equipos'][0]['gente'])} personas), "
          f"sin plannings.")
    print(f"  verificado: ninguno de los {len(reales)} nombres reales aparece en el archivo.")

    # megafonia-local.html ya no se regenera: era una copia con datos propios que
    # no se sincronizaba con el enlace, y tener dos plannings distintos sin
    # saberlo causó más problemas que los que resolvía. Ahora es un cartel que
    # lleva al enlace, y el ícono del Escritorio apunta directo ahí.


if __name__ == "__main__":
    main()

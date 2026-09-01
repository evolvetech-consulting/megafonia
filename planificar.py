#!/usr/bin/env python3
"""Genera el planning mensual de Megafonía y el mensaje listo para WhatsApp.

Uso:
    python3 planificar.py 2026-09
    python3 planificar.py 2026-09 --dias viernes,sabado
    python3 planificar.py 2026-09 --fechas 5,12,19,26
    python3 planificar.py 2026-09 --tarde-exclusiva
"""

import argparse
import calendar
import json
import random
import re
import sys
import unicodedata
from pathlib import Path

BASE = Path(__file__).resolve().parent
EQUIPO = BASE / "equipo.txt"
PLANNINGS = BASE / "plannings"

# Puesto -> (etiqueta para el mensaje, emoji, cuánta gente lleva)
PUESTOS = {
    "camara":     ("Cámara",     "🎥", 1),
    "audio":      ("Audio",      "🎙️", 1),
    "produccion": ("Producción", "🎛️", 1),
    "streaming":  ("Streaming",  "📡", 1),
    "tarde":      ("Tarde",      "🌇", 2),
}

DIAS = {"lunes": 0, "martes": 1, "miercoles": 2, "jueves": 3,
        "viernes": 4, "sabado": 5, "domingo": 6}

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def sin_tildes(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower())
                   if unicodedata.category(c) != "Mn")


# ── Carga del equipo ──────────────────────────────────────────────────────

def cargar_equipo():
    archivo = EQUIPO
    if not archivo.exists():
        # Recién clonado no hay equipo real: se corre con el de ejemplo.
        ejemplo = BASE / "equipo.ejemplo.txt"
        if not ejemplo.exists():
            sys.exit(f"No encuentro {EQUIPO.name}. Crealo antes de generar el planning.")
        print(f"  (no hay {EQUIPO.name}: usando {ejemplo.name}. "
              f"Copialo a {EQUIPO.name} y editalo con tu equipo.)\n")
        archivo = ejemplo

    miembros = []
    for nro, linea in enumerate(archivo.read_text(encoding="utf-8").splitlines(), 1):
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        if "|" not in linea:
            sys.exit(f"{archivo.name}:{nro}: falta el separador '|' → {linea}")

        nombre, crudo = (p.strip() for p in linea.split("|", 1))
        if not nombre:
            sys.exit(f"{archivo.name}:{nro}: la línea no tiene nombre")

        tokens = [sin_tildes(t) for t in re.split(r"[,\s]+", crudo) if t]
        puestos = set()
        for tok in tokens:
            quitar = tok.startswith("-")
            clave = tok.lstrip("-")
            destino = set(PUESTOS) if clave == "todos" else {clave}
            if clave != "todos" and clave not in PUESTOS:
                sys.exit(f"{archivo.name}:{nro}: puesto desconocido '{clave}'. "
                         f"Válidos: {', '.join(PUESTOS)}, todos")
            puestos -= destino if quitar else set()
            puestos |= set() if quitar else destino

        if not puestos:
            sys.exit(f"{archivo.name}:{nro}: {nombre} no quedó habilitado en ningún puesto")
        miembros.append({"nombre": nombre, "puestos": puestos})

    if not miembros:
        sys.exit(f"{archivo.name} no tiene ningún miembro activo.")
    return miembros


# ── Fechas del mes ────────────────────────────────────────────────────────

def fechas_del_mes(anio, mes, dias_semana, dias_explicitos):
    ultimo = calendar.monthrange(anio, mes)[1]
    if dias_explicitos:
        for d in dias_explicitos:
            if not 1 <= d <= ultimo:
                sys.exit(f"El día {d} no existe en {MESES[mes - 1]} {anio}.")
        return sorted(dias_explicitos)
    return [d for d in range(1, ultimo + 1)
            if calendar.weekday(anio, mes, d) in dias_semana]


def etiqueta_fecha(anio, mes, dia):
    nombre = ["Lunes", "Martes", "Miércoles", "Jueves",
              "Viernes", "Sábado", "Domingo"][calendar.weekday(anio, mes, dia)]
    return f"{nombre} {dia}"


# ── Historial (para equilibrar la carga entre meses) ──────────────────────

def cargar_historial():
    conteo = {}
    if PLANNINGS.exists():
        for archivo in sorted(PLANNINGS.glob("*.json")):
            try:
                datos = json.loads(archivo.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            for fecha in datos.get("fechas", []):
                for asignados in fecha.get("puestos", {}).values():
                    for nombre in asignados:
                        conteo[nombre] = conteo.get(nombre, 0) + 1
    return conteo


# ── Armado del planning ───────────────────────────────────────────────────

def armar(miembros, fechas, historial, tarde_exclusiva, rng):
    """Un intento de planning. Devuelve (asignaciones, huecos)."""
    veces_mes = {m["nombre"]: 0 for m in miembros}
    veces_puesto = {m["nombre"]: {} for m in miembros}
    ultima_fecha = {}
    plan, huecos = [], 0

    for idx, dia in enumerate(fechas):
        ocupados_manana, ocupados_tarde = set(), set()
        del_dia = {}

        for puesto, (_, _, cupo) in PUESTOS.items():
            elegidos = []
            for _ in range(cupo):
                es_tarde = puesto == "tarde"
                bloqueados = ocupados_tarde if (es_tarde and not tarde_exclusiva) \
                    else ocupados_manana | ocupados_tarde

                candidatos = [m for m in miembros
                              if puesto in m["puestos"]
                              and m["nombre"] not in bloqueados]
                if not candidatos:
                    huecos += 1
                    elegidos.append(None)
                    continue

                def costo(m):
                    n = m["nombre"]
                    c = (historial.get(n, 0) + veces_mes[n]) * 10
                    c += veces_puesto[n].get(puesto, 0) * 4      # rotar puestos
                    if ultima_fecha.get(n) == idx - 1:
                        c += 25                                   # evitar fechas seguidas
                    return c + rng.random()

                elegido = min(candidatos, key=costo)
                nombre = elegido["nombre"]
                elegidos.append(nombre)
                veces_mes[nombre] += 1
                veces_puesto[nombre][puesto] = veces_puesto[nombre].get(puesto, 0) + 1
                ultima_fecha[nombre] = idx
                (ocupados_tarde if es_tarde else ocupados_manana).add(nombre)

            del_dia[puesto] = elegidos

        plan.append({"dia": dia, "puestos": del_dia})

    return plan, huecos, veces_mes


def costo_global(huecos, veces_mes):
    """Menos huecos primero; después, el reparto más parejo posible."""
    valores = list(veces_mes.values())
    desbalance = max(valores) - min(valores) if valores else 0
    return (huecos * 1000) + (desbalance * 10) + sum(v * v for v in valores)


def mejor_planning(miembros, fechas, historial, tarde_exclusiva, intentos=3000):
    mejor = None
    for semilla in range(intentos):
        rng = random.Random(semilla)
        plan, huecos, veces = armar(miembros, fechas, historial, tarde_exclusiva, rng)
        puntaje = costo_global(huecos, veces)
        if mejor is None or puntaje < mejor[0]:
            mejor = (puntaje, plan, huecos, veces)
    return mejor[1], mejor[2], mejor[3]


# ── Salidas ───────────────────────────────────────────────────────────────

def mensaje_whatsapp(plan, anio, mes):
    lineas = [f"📢 *MEGAFONÍA — {MESES[mes - 1].upper()} {anio}*", ""]
    for fecha in plan:
        lineas.append(f"*{etiqueta_fecha(anio, mes, fecha['dia'])}*")
        for puesto, (etiqueta, emoji, _) in PUESTOS.items():
            gente = [n for n in fecha["puestos"][puesto] if n]
            texto = " – ".join(gente) if gente else "_a cubrir_"
            lineas.append(f"{emoji} {etiqueta}: {texto}")
        lineas.append("")
    lineas.append("Cualquier cambio, avisen con tiempo 🙏")
    return "\n".join(lineas)


def tabla_consola(plan, anio, mes, veces_mes):
    cols = ["Fecha"] + [PUESTOS[p][0] for p in PUESTOS]
    filas = []
    for fecha in plan:
        fila = [etiqueta_fecha(anio, mes, fecha["dia"])]
        for puesto in PUESTOS:
            gente = [n for n in fecha["puestos"][puesto] if n]
            fila.append(" – ".join(gente) if gente else "—")
        filas.append(fila)

    anchos = [max(len(f[i]) for f in [cols] + filas) for i in range(len(cols))]
    sep = "─┼─".join("─" * a for a in anchos)
    out = ["  " + " │ ".join(c.ljust(a) for c, a in zip(cols, anchos)),
           "  " + sep]
    out += ["  " + " │ ".join(c.ljust(a) for c, a in zip(f, anchos)) for f in filas]

    out.append("")
    out.append("  Reparto del mes:")
    for nombre, veces in sorted(veces_mes.items(), key=lambda kv: (-kv[1], kv[0])):
        out.append(f"    {nombre.ljust(max(len(n) for n in veces_mes))}  "
                   + "▪" * veces + f" {veces}")
    return "\n".join(out)


# ── Main ──────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Planning mensual de Megafonía")
    ap.add_argument("mes", help="mes a planificar, formato AAAA-MM (ej: 2026-09)")
    ap.add_argument("--dias", default="sabado",
                    help="días de servicio separados por coma (default: sabado)")
    ap.add_argument("--fechas", help="días concretos del mes, ej: 5,12,19,26 "
                                     "(tiene prioridad sobre --dias)")
    ap.add_argument("--tarde-exclusiva", action="store_true",
                    help="quien sirve a la mañana no puede repetir en el turno tarde")
    args = ap.parse_args()

    if not re.fullmatch(r"\d{4}-\d{2}", args.mes):
        sys.exit("El mes va en formato AAAA-MM. Ejemplo: 2026-09")
    anio, mes = (int(x) for x in args.mes.split("-"))
    if not 1 <= mes <= 12:
        sys.exit(f"'{mes}' no es un mes válido.")

    dias_semana = set()
    for d in args.dias.split(","):
        clave = sin_tildes(d.strip())
        if clave not in DIAS:
            sys.exit(f"Día desconocido '{d.strip()}'. Válidos: {', '.join(DIAS)}")
        dias_semana.add(DIAS[clave])

    explicitos = None
    if args.fechas:
        try:
            explicitos = [int(x) for x in args.fechas.split(",") if x.strip()]
        except ValueError:
            sys.exit("--fechas espera números separados por coma. Ejemplo: 5,12,19,26")

    fechas = fechas_del_mes(anio, mes, dias_semana, explicitos)
    if not fechas:
        sys.exit(f"No hay fechas de servicio en {MESES[mes - 1]} {anio}.")

    miembros = cargar_equipo()
    historial = cargar_historial()
    plan, huecos, veces_mes = mejor_planning(miembros, fechas, historial,
                                             args.tarde_exclusiva)

    print()
    print(f"  MEGAFONÍA — {MESES[mes - 1].upper()} {anio}"
          f"   ({len(miembros)} personas, {len(fechas)} fechas)")
    print()
    print(tabla_consola(plan, anio, mes, veces_mes))

    if huecos:
        print()
        print(f"  ⚠️  {huecos} puesto(s) sin cubrir: no hay suficiente gente "
              f"habilitada. Revisá equipo.txt.")

    PLANNINGS.mkdir(exist_ok=True)
    (PLANNINGS / f"{args.mes}.json").write_text(json.dumps(
        {"mes": args.mes, "fechas": plan}, ensure_ascii=False, indent=2),
        encoding="utf-8")

    texto = mensaje_whatsapp(plan, anio, mes)
    destino = PLANNINGS / f"{args.mes}-whatsapp.txt"
    destino.write_text(texto, encoding="utf-8")

    print()
    print("  ── Mensaje para WhatsApp " + "─" * 40)
    print()
    print(texto)
    print()
    print(f"  Guardado en {destino.relative_to(BASE)}")
    print(f"  Copiar al portapapeles:  pbcopy < \"{destino.relative_to(BASE)}\"")
    print()


if __name__ == "__main__":
    main()

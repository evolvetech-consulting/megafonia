# Megafonía

Planning mensual para un equipo de audiovisuales de iglesia: reparte los puestos
entre la gente disponible, deja ajustar a mano lo que haga falta y saca el
mensaje y la planilla listos para mandar al grupo de WhatsApp.

Nació para el equipo de megafonía de una iglesia adventista, pero sirve para
cualquier equipo que tenga que cubrir varios puestos fijos en fechas repetidas.

## Qué hace

- **Reparte solo.** Prueba 3000 combinaciones y se queda con la más pareja:
  equilibra cuántas veces sirve cada uno, rota los puestos para que no sea
  siempre el mismo en audio, y evita que la misma persona caiga dos fechas
  seguidas. Tiene en cuenta los meses anteriores, no solo el actual.
- **Respeta quién puede hacer qué.** Cada persona tiene sus puestos
  habilitados; los desplegables solo ofrecen a quien corresponde.
- **Avisa de los choques.** Si alguien queda en dos puestos el mismo día lo
  marca y lo explica. No bloquea: a veces se dobla a alguien a propósito.
- **Deshacer y rehacer** con Ctrl+Z / ⌘Z, incluso después de guardar.
- **Sale listo para mandar.** Texto con formato de WhatsApp, o la planilla del
  mes como imagen PNG para mandar como foto.

## Cómo se usa

Abrí `megafonia.html` con doble clic. Todo pasa en el navegador: no hay
servidor, no hay que instalar nada, los datos se guardan en esa máquina.

Trae un equipo de ejemplo. Andá a **Equipo**, borralo y cargá el tuyo:

- Tocá los puestos de cada persona para habilitarlos o quitarlos.
- **◉** la da de baja sin borrarla (vacaciones, un viaje); **✕** la saca del equipo.
- Elegí qué días de la semana hay servicio.
- La regla de tarde exclusiva decide si quien sirve a la mañana puede repetir
  a la tarde.

Después, en **Planning**, tocá **Generar**. Ajustá lo que quieras con los
desplegables y guardá. En **Compartir** tenés el texto y la imagen.

Desde **Equipo → Copia de seguridad** exportás todo a un JSON, que sirve de
respaldo y para pasar los datos a otra máquina o navegador.

## La versión de terminal

`planificar.py` hace el reparto desde la línea de comandos, leyendo el equipo de
un archivo de texto:

```sh
cp equipo.ejemplo.txt equipo.txt     # y editalo con tu gente
python3 planificar.py 2026-09
python3 planificar.py 2026-09 --dias viernes,sabado
python3 planificar.py 2026-09 --fechas 5,12,19,26
python3 planificar.py 2026-09 --tarde-exclusiva
```

Solo necesita Python 3, sin dependencias. Guarda cada mes en `plannings/` y
escribe el mensaje de WhatsApp en un `.txt` aparte.

## Los datos no están acá

Este repo tiene el código y un equipo inventado. Los nombres reales de un equipo
no se publican: viven en el navegador de quien usa la app y, si se usa alojada,
en esa copia privada.

`.gitignore` excluye `app.html`, `equipo.txt`, `plannings/` y las exportaciones.
Si trabajás sobre una copia con datos reales, `hacer-plantilla.py` regenera
`megafonia.html` reemplazando el equipo por el de ejemplo, y aborta si algún
nombre real sobrevive al reemplazo.

## Créditos

El símbolo adventista (`logo-adventista.svg`) viene de
[Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Adventist_Symbol.svg),
en dominio público. Es marca registrada de la Corporación General de la Iglesia
Adventista del Séptimo Día: si lo usás, respetá sus normas de identidad — no lo
recortes, no le cambies el color ni lo deformes.

Tipografías Archivo e IBM Plex, vía Google Fonts.

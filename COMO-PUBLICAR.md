# Poner la app en tu propio sitio

Tres pasos. La app queda en una dirección tuya, con su icono y su nombre, y los
datos en una base propia que sincroniza todos los dispositivos.

## 1. La base — Supabase

1. Entrá a [supabase.com](https://supabase.com) y creá una cuenta (gratis).
2. **New project**. Ponele nombre `megafonia`, elegí una contraseña para la base
   (guardala, no la vas a necesitar seguido) y la región más cercana.
3. Cuando termine de crearse, andá a **SQL Editor** → **New query**, pegá todo el
   contenido de `base-de-datos.sql` y tocá **Run**. Debería decir *Success*.
4. Andá a **Project Settings → API** y copiá dos cosas:
   - **Project URL** — algo como `https://abcdefgh.supabase.co`
   - **anon public** — una clave larga que empieza con `eyJ`

Pasame esos dos valores y los dejo puestos en la app.

## 2. El sitio — Netlify

1. Entrá a [netlify.com](https://netlify.com) y creá una cuenta.
2. **Add new site → Import an existing project → GitHub**.
3. Autorizá el acceso y elegí el repositorio `megafonia`.
4. No toques nada de la configuración: ya está en `netlify.toml`.
5. **Deploy**.

En un minuto te da una dirección tipo `megafonia-abc123.netlify.app`. Podés
cambiarla en **Site configuration → Change site name** por algo como
`megafonia-malaga`.

## 3. Llevar el planning

Los datos actuales están en la app de claude.ai. Para pasarlos:

1. En la app vieja: **Equipo → Copia de seguridad → Exportar datos**
2. En la nueva: **Equipo → Copia de seguridad → Importar datos**
3. **Guardar**

Listo. De ahí en más la app vieja queda sin uso.

## Qué cambia

- El icono y el nombre en la pantalla de inicio son los tuyos.
- El enlace lo abre cualquiera, sin cuenta de nada.
- Sigue sincronizando entre la PC y el celular, ahora contra tu base.

## Tener presente

**El enlace da permiso de editar.** Quien lo tenga puede cambiar el planning, no
solo verlo. Para el grupo de la iglesia alcanza, pero no lo publiques en un
lugar abierto. Si más adelante querés que el equipo solo pueda marcar «no
puedo» y no tocar el resto, se puede separar: avisá y lo ajustamos.

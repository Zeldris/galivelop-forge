# Aviso para gart (galivelop-artifacts)

**De:** galivelop-forge (`gforge`) · **Fecha:** 2026-11-27 · **Estado:** pendiente de llevar a gart · **Tarea:** 0.1.0-2

Desde forge no se modifica gart: este aviso lo lleva la persona o una sesión que trabaje en gart. Se escribió tras leer
gart en `main` 2eca8da (solo documentación y flujo, sin código).

## Lo que forge pide

1. **Alta del espacio `gforge`**, con forge como dueño único (la regla «solo su dueño publica en él»). KindIds
   previstos, todos provisionales (`/0`): `gforge.dataset/0`, `gforge.recipe/0`, `gforge.training/0`,
   `gforge.card/0` (`docs/ddd.md` de forge, §4). Hoy gart no tiene registro de espacios ni procedimiento de alta
   (su ADR 0004: «no hay registro central»), así que habría que decidir dónde queda apuntado.
2. **Una primera versión del validador que se pueda vendorizar**: el paquete `gart` con `KindId`, `validate` y
   `ValidationError`, que describe su DDD (§5-§6), y su número de versión declarado en algún sitio (hoy no hay ninguno).
3. **Concretar el ADR 0002** (copia vendorizada con versión y test de huella sha256), que no dice qué se copia ni
   qué se hashea. Propuesta de forge, para que gart la acepte o la cambie:
   - gart publica cada versión con una etiqueta `vX.Y.Z` y, en ella, un `SHA256SUMS` (formato de `sha256sum`) con una
     línea por cada archivo del paquete `gart/`.
   - El consumidor copia el paquete tal cual en `vendor/gart/`, con `VERSION` (versión y commit de origen) y el
     `SHA256SUMS` de esa etiqueta.
   - El test del consumidor rehace el sha256 de cada archivo de `vendor/gart/` y lo compara con `SHA256SUMS`;
     falla si un archivo cambió, falta o sobra, y nombra el archivo.
   - Actualizar la copia es cambiar los tres juntos (paquete, `VERSION`, `SHA256SUMS`) en un solo commit.
4. **Licencia:** gart no tiene archivo `LICENSE` (su ADR 0006 dice «la misma licencia que los demás repos
   Galivelop», sin fijarla). Sin licencia escrita, forge no puede vendorizar la copia ni declararla en `THIRD-PARTY.md`.
5. **Versión de Python:** el DDD de gart dice «Python ≥ 3.10»; el núcleo de forge promete 3.8+ (`pyproject.toml`).
   O el validador evita lo que exige 3.10 (`match`, `X | Y` en anotaciones evaluadas…), o forge sube su mínimo a
   3.10; forge prefiere lo primero. Hay que decidirlo antes de vendorizar.

## Qué hace forge mientras

Las tareas 0.1.0-2 (vendorizar) y 0.1.0-3 (esquema `gforge.dataset/0` validado en gart) quedan bloqueadas; forge
sigue con 0.1.0-4 a 0.1.0-7, que no dependen de gart (respuestas a Q-1..Q-3, `docs/questions.md`).

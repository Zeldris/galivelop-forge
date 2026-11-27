# Pendiente

Lo que queda abierto; la bitácora solo apunta aquí. Se añade y se quita en este archivo.

## Pendiente

- **Flujo (Galivelop-workflow), revisión 0.0.1-5, medio:** el matcher de `review-before-main.sh` en
  `.claude/settings.json` solo casa con `mcp__github__…`; un servidor con otro prefijo se salta la marca. Arreglar en
  el repo del flujo y reinstalar.
- **Flujo, medio:** `push_files` y `create_or_update_file` con `branch: main` (o vacío) escriben en `main` sin
  `pre-push` ni marca; añadirles una guarda en el flujo.
- **Flujo, medio:** en `.github/workflows/check.yml`, `bash -c "$cmd"` hereda el here-string como stdin; un comando
  que lea stdin se come el resto del check. Arreglo: `</dev/null`. En el flujo.
- **Flujo, W5 (nota para el repo del flujo), leve:** correr el check en Python 3.8 de verdad: `ubuntu-latest` (26.04) ya no trae 3.8 en `setup-python` (probado 2026-11-27, CI rojo); hace falta un runner `ubuntu-22.04`/`24.04` fijo o un contenedor. Hoy solo `tests/test_py38_syntax.py` lo aproxima.
  `check.yml` es del flujo (`apply.py`, v0.9.1) y sin `pyproject.toml`/`requirements*.txt` `setup-python` se salta, así que
  `ciPython` no basta: pedir al flujo un `ciRunner` o un job en contenedor con 3.8. No se edita `check.yml` aquí.
- **Leve:** registrar `docs/roadmap.md` en `plan`/`roadmapFiles` de `.claude/gw.json` cuando se compruebe que su
  formato casa con lo que espera el flujo.
- **0.1.0-6, observación:** `_seed` trata igual `1` y `"1"`; un kill duro puede dejar un `.build-*` huérfano (no se puede cubrir).

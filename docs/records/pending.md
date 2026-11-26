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
- **F1 (0.1.0-1), leve:** `tests/test_smoke.py` es de relleno y no puede fallar; con el `pyproject.toml` fijar
  `ciPython: ["3.8", "3.x"]` para comprobar de verdad Python 3.8.
- **Leve:** registrar `docs/roadmap.md` en `plan`/`roadmapFiles` de `.claude/gw.json` cuando se compruebe que su
  formato casa con lo que espera el flujo.

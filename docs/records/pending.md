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
- **F1, leve:** correr el check en Python 3.8 de verdad: `ubuntu-latest` (26.04) ya no trae 3.8 en `setup-python` (probado 2026-11-27, CI rojo); hace falta un runner `ubuntu-22.04`/`24.04` fijo o un contenedor. Hoy solo `tests/test_py38_syntax.py` lo aproxima.
- **Leve:** registrar `docs/roadmap.md` en `plan`/`roadmapFiles` de `.claude/gw.json` cuando se compruebe que su
  formato casa con lo que espera el flujo.
- **0.1.0-5, leve:** `origin=synthetic` lo decide una marca que un jugador puede escribir: no es garantía de contenido
  sintético; documentarlo, o no fiarse solo de ella cuando se trate aparte lo `live`.
- **0.1.0-5, leve:** los patrones abiertos de `gforge/teachers.py` con comodín inicial aceptan cualquier modelo que
  contenga la subcadena, y llama-3.2 visión / deepseek-r1-distill-llama tienen licencia propia: anclarlos al resolver Q-6.
- **0.1.0-5, leve:** `_narration` acepta una `narration` vacía: decidir si se rechaza.
- **0.1.0-5, leve:** `read_distillation` ignora sin avisar lo que no termina en `.jsonl` (p. ej. `Cat.JSONL`).
- **0.1.0-6, observación:** `_seed` trata igual `1` y `"1"`; un kill duro puede dejar un `.build-*` huérfano (no se puede cubrir).
- **F1, leve (revisión fase 3 de 9bf05c9):** `_publish` sustituye en silencio un directorio de versión vacío ya existente en POSIX (en Windows falla); añadir el test del caso vacío o aceptar la diferencia. Nota: con `CC-BY-SA-4.0` en una fuente `build` nunca puede construir (falla cerrado frente a la licencia NC-SA del contenido); decirlo en la ficha de 0.1.0-8.

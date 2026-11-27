<!-- galivelop-workflow v0.9.1 -->
# gw-opt-tokens — notas del proyecto

Las lee la skill `gw-opt-tokens` antes de proponer nada, y se actualizan cuando la persona aprueba un cambio. El flujo
las crea una vez; desde entonces son del proyecto.

## Herramientas que ya ahorran

<!-- Una línea cada una, con cómo se corre. -->
- `python3 .claude/gw/scripts/recover.py --state` y `--search "<texto>"`: recuperar lo que se llevó una
  compactación.
- `gw-orchestrate-dealer`: el trabajo de más de un paso, repartido a subagentes de contexto limpio.

## Costes conocidos

<!-- Lo que se ha visto que cuesta mucho en este proyecto (archivos grandes leídos enteros, salidas largas...). -->
- El arranque fijo (prompt, herramientas, MCP) es ~95 k por llamada, el 81 % de la entrada; en Claude en la nube los
  conectores no se pueden desactivar (T1 rechazada): solo baja con menos llamadas.
- `AGENTS.md` se leyó 12 veces en una sesión: se lee una vez por tarea; para una regla puntual, `grep -n` (T3).

## Ajustes en vigor

- Ventana de compactación automática: `CLAUDE_CODE_AUTO_COMPACT_WINDOW` en `.claude/settings.json`.

## Referencias medidas

<!-- Cifras medidas con las que comparar: fecha, sesión, contexto medio, llamadas, total. -->
- 2026-11-26, sesión a54c4183 (instalación, F-1, F0): 64 llamadas, contexto medio 117 k, 7,48 M de entrada; con
  los subagentes, 10,08 M.
- 2026-11-27, sesión e13ef396 (bloque 0.1.0, revisión y arreglos): 16 llamadas, contexto medio 96 k (84 % arranque
  fijo), 1,53 M de entrada; con los subagentes (reviewer sonnet 5 llamadas, worker opus 9), 1,95 M.

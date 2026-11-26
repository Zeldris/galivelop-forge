<!-- galivelop-workflow v0.9.1 -->
# Bitácora (traspaso)

> Léela entera al empezar cualquier sesión. Lo que no está subido no existe: commit + push en cada punto estable,
> con esta bitácora actualizada en el mismo commit. El flujo nunca la sobrescribe una vez creada.

## Estado actual

| Campo | Valor |
|---|---|
| **Rama** | `ccr-9d1db1a5-uvw2uh` |
| **Fase / tarea** | Instalación de Galivelop-workflow v0.9.1 hecha; F-1 (mejorar, ampliar y cerciorar `docs/ddd.md`) pendiente; luego F0 (decisiones a `main`, reparto en versiones). |
| **Último punto estable** | El commit de instalación del flujo (workflow v0.9.1, licencias, DDD borrador 1). |
| **Siguiente paso** | F-1: repasar `docs/ddd.md` sección a sección con la persona (skill `grill-with-docs`), contrastando con los DDD de gart, gmod, grun y GVE mediante subagentes, y cerrar las preguntas de §8. |
| **Check** | `python3 -m unittest discover -s tests`, `python3 .claude/gw/scripts/tests-after-main.py`, `python3 .claude/gw/scripts/ci-local.py --validate`: verde (solo `tests/test_smoke.py`: deuda hasta que exista `gforge` en F1). |

## Para la próxima publicación

F0: el DDD con las decisiones de §8 cerradas y el reparto en versiones; espera a F-1.

## Hecho (5 últimas)

1. 2026-11-26 — Galivelop-workflow v0.9.1 instalado (`/gw-init`), licencia MIT + CC BY-NC-SA 4.0, DDD borrador 1 en `docs/ddd.md`.

## Pendiente

Lo pendiente está en el archivo de `pendingFile` (`.claude/gw.json`; por defecto `docs/records/pending.md`): decisiones de la persona que bloquean algo, problemas conocidos, ideas sin planificar. Se añade y se quita allí; `handoff.py move-pending` rehace esta línea y `handoff.py add-pending "texto"` añade sin leer el archivo.

## Comprobar el estado

- Últimos commits: `git fetch origin <rama> && git log --oneline -5 origin/<rama>`.
- El check: `python3 -m unittest discover -s tests`, `python3 .claude/gw/scripts/tests-after-main.py`, `python3 .claude/gw/scripts/ci-local.py --validate`.
- Flujo bien montado: `python3 .claude/gw/scripts/doctor.py`.
- Estado de la bitácora tal como lo recibe una sesión nueva: `python3 .claude/gw/scripts/recover.py --state`.

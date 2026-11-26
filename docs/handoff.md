<!-- galivelop-workflow v0.9.1 -->
# Bitácora (traspaso)

> Léela entera al empezar cualquier sesión. Lo que no está subido no existe: commit + push en cada punto estable,
> con esta bitácora actualizada en el mismo commit. El flujo nunca la sobrescribe una vez creada.

## Estado actual

| Campo | Valor |
|---|---|
| **Rama** | `ccr-9d1db1a5-uvw2uh` |
| **Fase / tarea** | Versión 0.0.1 (F-1 + F0) cerrada y en `main` (d31f9f8, 2026-11-26, con confirmación de la persona). Siguiente versión: 0.1.0 (F1, datos). |
| **Último punto estable** | `main` = d31f9f8 (marca de revisión de 5a343ef). |
| **Siguiente paso** | `/clear` y abrir la 0.1.0 con `docs/roadmap.md`: empezar por 0.1.0-1 (paquete `gforge` stdlib, puertos que fallan cerrados, test de importación limpia). Pendientes en `docs/records/pending.md`. |
| **Check** | `python3 -m unittest discover -s tests`, `python3 .claude/gw/scripts/tests-after-main.py`, `python3 .claude/gw/scripts/ci-local.py --validate`: verde (solo `tests/test_smoke.py`: deuda hasta que exista `gforge` en F1). |

## Para la próxima publicación

F0: el DDD con las decisiones de §8 cerradas y el reparto en versiones; espera a F-1.

## Hecho (5 últimas)

1. 2026-11-26 — Galivelop-workflow v0.9.1 instalado (`/gw-init`), licencia MIT + CC BY-NC-SA 4.0, DDD borrador 1 en `docs/ddd.md`.

## Pendiente

Lo pendiente está en [`docs/records/pending.md`](records/pending.md); se añade y se quita allí.

## Comprobar el estado

- Últimos commits: `git fetch origin <rama> && git log --oneline -5 origin/<rama>`.
- El check: `python3 -m unittest discover -s tests`, `python3 .claude/gw/scripts/tests-after-main.py`, `python3 .claude/gw/scripts/ci-local.py --validate`.
- Flujo bien montado: `python3 .claude/gw/scripts/doctor.py`.
- Estado de la bitácora tal como lo recibe una sesión nueva: `python3 .claude/gw/scripts/recover.py --state`.

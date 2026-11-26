<!-- galivelop-workflow v0.9.1 -->
# Bitácora (traspaso)

> Léela entera al empezar cualquier sesión. Lo que no está subido no existe: commit + push en cada punto estable,
> con esta bitácora actualizada en el mismo commit. El flujo nunca la sobrescribe una vez creada.

## Estado actual

| Campo | Valor |
|---|---|
| **Rama** | `ccr-9d1db1a5-uvw2uh` |
| **Fase / tarea** | Versión 0.1.0 (F1, datos). 0.1.0-1 hecha: paquete `gforge` (stdlib), cinco puertos que fallan cerrados, servicios `baseline` y `train`, tests de las invariantes 7 y 10. Presupuesto de compactaciones: 1 (para la 0.1.0 entera). |
| **Último punto estable** | Este commit (0.1.0-1). `main` = d31f9f8. |
| **Siguiente paso** | 0.1.0-2: vendorizar gart con su test de huella sha256 y pedir el alta del espacio `gforge` en gart (leer gart con un subagente; desde aquí no se modifica). |
| **Check** | `python3 -m unittest discover -s tests`, `python3 .claude/gw/scripts/tests-after-main.py`, `python3 .claude/gw/scripts/ci-local.py --validate`: verde (9 tests). |

## Para la próxima publicación

F0: el DDD con las decisiones de §8 cerradas y el reparto en versiones; espera a F-1.

## Hecho (5 últimas)

1. 2026-11-26 — 0.1.0-1: paquete `gforge` con `pyproject.toml`, `ports.py` (`PortUnavailable` y los puertos `Unavailable*`), `services.py`; `tests/test_smoke.py` sustituido.
2. 2026-11-26 — Galivelop-workflow v0.9.1 instalado (`/gw-init`), licencia MIT + CC BY-NC-SA 4.0, DDD borrador 1 en `docs/ddd.md`.

## Pendiente

Lo pendiente está en [`docs/records/pending.md`](records/pending.md); se añade y se quita allí.

## Comprobar el estado

- Últimos commits: `git fetch origin <rama> && git log --oneline -5 origin/<rama>`.
- El check: `python3 -m unittest discover -s tests`, `python3 .claude/gw/scripts/tests-after-main.py`, `python3 .claude/gw/scripts/ci-local.py --validate`.
- Flujo bien montado: `python3 .claude/gw/scripts/doctor.py`.
- Estado de la bitácora tal como lo recibe una sesión nueva: `python3 .claude/gw/scripts/recover.py --state`.

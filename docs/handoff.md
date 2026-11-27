<!-- galivelop-workflow v0.9.1 -->
# Bitácora (traspaso)

> Léela entera al empezar cualquier sesión. Lo que no está subido no existe: commit + push en cada punto estable,
> con esta bitácora actualizada en el mismo commit. El flujo nunca la sobrescribe una vez creada.

## Estado actual

| Campo | Valor |
|---|---|
| **Rama** | `claude/siguiente-ftxnzk` (sigue a `ccr-9d1db1a5-uvw2uh`, traída por fast-forward) |
| **Fase / tarea** | Versión 0.1.0 (F1, datos). Hechas 0.1.0-1, 0.1.0-4, 0.1.0-5, 0.1.0-6 y 0.1.0-7 (`gforge.datasets`; `gforge.splits`; `gforge.filters`: correos, teléfonos y nombres de una lista que da quien llama, fuera del repo; `gforge.teachers`: lista de maestros abiertos que falla cerrada). 0.1.0-2/3 bloqueadas por gart. Q-6 abierta: confirmar la lista de maestros. Presupuesto de compactaciones: 1 (para la 0.1.0 entera). |
| **Último punto estable** | 0.1.0 cerrada y en `main` = 74c2004 (subida directa, confirmada por la persona; CI verde, marca de revisión `74c2004`). |
| **Siguiente paso** | Empezar la 0.2.0 (según `docs/plan`) desde `main` con `merge-main.py`. 0.1.0-2/3 siguen bloqueadas por gart; leves de la revisión en `docs/records/pending.md`; Python 3.8 en el CI, pendiente. |
| **Check** | `python3 -m unittest discover -s tests`, `python3 .claude/gw/scripts/tests-after-main.py`, `python3 .claude/gw/scripts/ci-local.py --validate`: verde (63 tests). |

## Para la próxima publicación

F0: el DDD con las decisiones de §8 cerradas y el reparto en versiones; espera a F-1.

## Hecho (5 últimas)

1. 2026-11-27 — 0.1.0-7: `gforge/datasets.py`: `build` (criba, parte, escribe `datasets/<objetivo>/<versión>/` con `LICENSE` y `manifest.json` `gforge.dataset/0`), `combine`/`model_licence` (unión de condiciones; licencia desconocida o ausente falla), la versión no se sobrescribe, los rechazados van por id y regla sin texto.
2. 2026-11-27 — 0.1.0-6: particiones deterministas (`gforge/splits.py`): cubo = sha256(semilla, id), test < val < train; id repetido o semilla vacía fallan con motivo.
3. 2026-11-27 — 0.1.0-5: filtros de datos personales y de maestro (`gforge/filters.py`, `gforge/teachers.py`); `pyproject.toml` empaqueta también `gforge.sources`.
4. 2026-11-26 — 0.1.0-2: gart leído con un subagente; sin código, ADR 0002 sin detalle del test de huella, sin LICENSE ni registro de espacios. Preguntas Q-1..Q-3, respondidas: seguir con 0.1.0-4..7 y aviso a gart escrito (`docs/records/aviso-gart.md`, con el choque Python 3.10 frente a 3.8).
5. 2026-11-26 — 0.1.0-1: paquete `gforge` con `pyproject.toml`, `ports.py` (`PortUnavailable` y los puertos `Unavailable*`), `services.py`; `tests/test_smoke.py` sustituido.

## Pendiente

Lo pendiente está en [`docs/records/pending.md`](records/pending.md); se añade y se quita allí.

## Comprobar el estado

- Últimos commits: `git fetch origin <rama> && git log --oneline -5 origin/<rama>`.
- El check: `python3 -m unittest discover -s tests`, `python3 .claude/gw/scripts/tests-after-main.py`, `python3 .claude/gw/scripts/ci-local.py --validate`.
- Flujo bien montado: `python3 .claude/gw/scripts/doctor.py`.
- Estado de la bitácora tal como lo recibe una sesión nueva: `python3 .claude/gw/scripts/recover.py --state`.

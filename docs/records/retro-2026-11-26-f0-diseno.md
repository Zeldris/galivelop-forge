# Retro 2026-11-26: instalación, F-1 y F0 (versión 0.0.1)

**Estado:** pendiente de la persona.

Sesión `a54c4183`: instalación del flujo, DDD borrador 2, ADR 0001-0013, reglas, roadmap y revisión del bloque.
Gasto medido con `gw-opt-tokens` (`measure.py --hours 0`): sesión principal, 64 llamadas, 7,48 M de entrada, contexto
medio 117 k; subagentes, 2,60 M. El arranque fijo (prompt del sistema, herramientas, MCP) son ~94,7 k por llamada,
el 81 % de la entrada; el proyecto, el 19 %. El registro de desvíos está vacío.

## Propuestas de gasto (gw-opt-tokens)

- **T1. Desactivar los conectores y servidores MCP que no se usan en este repo** (Claude Docs, entre otros; los
  muestra `/context`). Es lo que más pesa: el 81 % de la entrada es el arranque fijo, y 20 k menos por llamada son
  ~1,3 M por sesión como esta. Lo hace la persona en la configuración. *Coste:* ninguno. *Riesgo de calidad:*
  ninguno si se deja GitHub y `claude-code-remote`; un conector desactivado se vuelve a activar cuando haga falta.
- **T2. Leer los otros repos solo con un subagente, también durante la instalación.** El `SKILL.md` de `gw-init`
  leído en la sesión principal arrastró 93 k; `apply.py --help` y `THIRD-PARTY.md`, otros 84 k. El gancho ya avisa;
  falta que `gw-init` lo diga en su primer paso. *Salida:* el flujo. *Riesgo:* ninguno.
- **T3. Que `AGENTS.md` se lea una vez por tarea**: se leyó 12 veces (43 k arrastrados). Para lo puntual, `grep -n`
  sobre la regla. *Salida:* nota en `.claude/gw/gw-opt-tokens.md`. *Riesgo:* ninguno.

## Propuestas del entorno (retro)

- **R1, automatizar (flujo).** El `AGENTS.md` instalado listaba dos órdenes del check y `gw.json` tenía tres, y nada
  lo detectó (hallazgo 6 de la revisión). Propuesta: `doctor.py` compara las órdenes del check de `AGENTS.md` con
  `check` de `gw.json`. *Salida:* el flujo.
- **R2, instalación (flujo).** `gw-init` deja `taskId` en `[A-Z]{2,5}-\d+` sin preguntar la forma de los ids; aquí
  son semver (`0.0.1-5`). Propuesta: `gw-init` pregunta la forma de los ids, o deriva `taskId` del roadmap. *Salida:*
  el flujo.
- **R3, guardas (flujo).** Los hallazgos medios 1-3 de la revisión, ya en `docs/records/pending.md`. *Salida:* el
  flujo.
- **R4, proyecto.** `requireRetro` estaba desactivado; ya está a `true` (commit 659f669). Sin más acción.
- **Barrido de leves:** ningún script del proyecto tiene dos leves abiertos o más; no hay barrido que proponer.

## For Galivelop-workflow

- `gw-init`: leer el repo del flujo con un subagente desde el primer paso (T2).
- `doctor.py`: comprobar que las órdenes del check de `AGENTS.md` coinciden con `check` de `gw.json` (R1).
- `gw-init`: preguntar la forma de `taskId` o derivarla del roadmap (R2).
- `review-before-main.sh`: matcher para cualquier prefijo de servidor GitHub; guarda para `push_files` y
  `create_or_update_file` sobre la rama protegida; `check.yml` con `bash -c "$cmd" </dev/null` (R3).

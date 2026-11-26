<!-- galivelop-workflow v0.9.1 -->
# Glosario

Vocabulario de galivelop-forge. Primero van los términos del flujo; el proyecto añade debajo los de su dominio y los
mantiene al día (skill `domain-modeling`). El flujo nunca sobrescribe este archivo una vez creado.

## Términos del flujo

- **Bitácora**: `docs/handoff.md`, el estado del trabajo para la siguiente sesión: rama, tarea en curso, siguiente paso,
  check.
- **Relevo**: una sesión que se acaba y otra que sigue desde la bitácora, sin preguntar por dónde iba.
- **Punto estable**: un estado con el check en verde, con commit y subido.
- **Check**: las órdenes del proyecto que tienen que pasar en cada commit que se sube: `python3 -m unittest discover -s tests`, `python3 .claude/gw/scripts/tests-after-main.py`, `python3 .claude/gw/scripts/ci-local.py --validate`.
- **Commit `WIP:`**: un commit subido con algo a medias o en rojo; la bitácora dice qué falla y por qué.
- **Rama protegida**: `main`, lo publicado; solo recibe trabajo revisado, con confirmación
  de la persona.
- **Marca de revisión**: `docs/records/reviewed.txt`, el archivo versionado con el sha del último commit revisado; los ganchos
  aceptan código hasta él.
- **Contenido frente a código**: el contenido (lo que casa con `content` de `.claude/gw.json`) no necesita revisión
  de código; todo lo demás es código.
- **Encargo a un subagente**: lo que recibe un subagente: objetivo, rutas, restricciones, el check que debe pasar y
  qué tiene que devolver.
- **Retro**: la retrospectiva de la sesión antes de ir a la rama protegida; sus propuestas se presentan a la persona y
  lo que confirme se aplica en la rama.
- **Propuesta (`.gw-new`)**: un archivo del flujo que la actualización no pudo aplicar sin perder cambios locales;
  se fusiona a mano y luego se borra.

## Términos del proyecto

<!-- **Término**: definición, y dónde vive en el código. -->

- **Puerto no disponible**: la forma por defecto de cada puerto (`Unavailable<Puerto>`); toda operación lanza
  `PortUnavailable` con el puerto, lo que falta y la orden o el repo que lo arregla (invariante 10). `gforge/ports.py`.

Tomado de `docs/ddd.md` §2 (F-1 cerrada). Aún no hay código.

- **Fuente** (`Source`): adaptador que lee los datos crudos de una aplicación.
- **Ejemplo** (`Example`): pareja entrada→salida (SFT) o entrada→elegida/rechazada (DPO), con procedencia.
- **Maestro** (`Teacher`): modelo abierto que generó la salida de un ejemplo y permite entrenar con ella.
- **Dataset** (`Dataset`): conjunto versionado de ejemplos, con licencia, procedencia, hash y particiones.
- **Partición** (`Split`): train / val / test, decidida por la semilla y el hash del ejemplo.
- **Peldaño** (`Rung`): nivel de ajuste: `prompt`, `modelfile`, `sft`, `dpo`.
- **Receta** (`Recipe`): peldaño, modelo base, dataset, hiperparámetros y semilla.
- **Entrenamiento** (`TrainingRun`): ejecución de una receta: estado, máquina, duración, pesos. No es la «corrida» del GVE.
- **Medida** (`Measure`): lo que forge recibe del GVE: una `gve.evidence/1` y, frente a otra, una `gve.comparison/1`.
- **Línea base** (`Baseline`): medida del GVE del modelo sin ajustar.
- **Umbral** (`Threshold`): mínimo absoluto opcional del objetivo, además de la regla de demostración del GVE.
- **Escalera** (`Ladder`): secuencia de peldaños de un objetivo, con su medida.
- **Ficha** (`Card`): model card publicable.
- **Objetivo** (`Target`): tarea concreta a mejorar (p. ej. `tarkor.narrator`).
- **Puerto** (`Port`): interfaz de forge hacia otro repo (`MachinePort`, `QueuePort`, `MeasurePort`, `TrainerPort`, `PublishPort`); sin el repo, falla cerrado.

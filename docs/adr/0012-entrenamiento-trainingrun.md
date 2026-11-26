# La ejecución de una receta se llama Entrenamiento

<!-- gvc-ddd-decision: q12 -->
Status: accepted

Sección de origen: §2, §4

## Contexto

El borrador 1 llamaba `Run` a la ejecución de una receta, y el nombre choca con otros repos.

## Decisión

Se llama `Entrenamiento` (`TrainingRun`, `gforge.training/0`). «Corrida» queda para el GVE y `gdev.run/0` para developer.

## Consecuencias

El glosario y los artefactos usan `TrainingRun`; `Run` desaparece.

# Solo maestros abiertos como fuente de datos

<!-- gvc-ddd-decision: q7 -->
Status: accepted

Sección de origen: §2, §5.9

## Contexto

Los ejemplos pueden generarse con modelos cuyos términos prohíben entrenar con sus salidas.

## Decisión

No se aceptan salidas de modelos cerrados. Solo maestros abiertos cuyos términos permiten entrenar con sus salidas; cada ejemplo nombra a su maestro (invariante 9). Sigue la decisión de galivelop-developer.

## Consecuencias

El ingest rechaza los ejemplos con maestro prohibido (Claude, GPT…) o sin maestro declarado.

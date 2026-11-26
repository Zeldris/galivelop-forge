# La escalera: prompt, modelfile, sft, dpo

<!-- gvc-ddd-decision: q9 -->
Status: accepted

Sección de origen: §2, §6

## Contexto

Había que fijar los peldaños de la escalera de ajuste.

## Decisión

`prompt` → `modelfile` → `sft` (LoRA/QLoRA) → `dpo`. RAG, salidas estructuradas y verificador son del sistema de la aplicación; la línea base se mide con ellos puestos.

## Consecuencias

La escalera empieza en el prompt. Ese sistema alrededor del modelo queda fuera del alcance de forge.

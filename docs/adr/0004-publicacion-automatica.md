# Publicación automática en Hugging Face con medida en verde

<!-- gvc-ddd-decision: q4 -->
Status: accepted

Sección de origen: §3, §5.4

## Contexto

Había que decidir si publicar en Hugging Face a mano o de forma automática.

## Decisión

La publicación es automática cuando el entrenamiento cumple la invariante 4 (medida válida y `demonstrated`). Sin credencial de Hugging Face, `publish` falla cerrado.

## Consecuencias

`publish` no pide intervención, pero nada se publica sin medida. Hay que actualizar AGENTS.md y REVIEW.md (nada sale a Hugging Face sin confirmación, regla actual del proyecto).

# Los datasets viven en el repo de forge

<!-- gvc-ddd-decision: q2 -->
Status: accepted

Sección de origen: §3, §6

## Contexto

Los datasets de Tarkor son contenido CC BY-NC-SA, y hay que decidir dónde se guardan.

## Decisión

Viven en el repo de forge, en `datasets/`, bajo la licencia de contenido CC BY-NC-SA 4.0, la misma que Tarkor. No hay servicio externo para los datos. Git LFS solo si un archivo pasa del umbral del flujo.

## Consecuencias

El contexto Dataset guarda `datasets/<objetivo>/<versión>/`. El código es MIT y el contenido, datasets incluidos, CC BY-NC-SA 4.0.

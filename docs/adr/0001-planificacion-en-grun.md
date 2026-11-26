# La planificación entre aplicaciones no es de forge

<!-- gvc-ddd-decision: q1 -->
Status: accepted (provisional hasta el DDD de grun)

Sección de origen: §3, §6

## Contexto

Varias aplicaciones de Galivelop pueden querer la GPU de una misma máquina. grun (hoy vacío) tiene la cola y el cerrojo de GPU.

## Decisión

forge es un cliente más de la cola de grun. Las prioridades entre aplicaciones son de grun o de un repo futuro, no de forge. Es provisional: se revisa cuando grun tenga DDD.

## Consecuencias

forge no implementa planificador. Queda fuera de alcance (§6). La decisión se reabre con el DDD de grun.

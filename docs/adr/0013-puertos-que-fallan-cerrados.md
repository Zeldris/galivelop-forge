# Puertos que fallan cerrados mientras gmod y grun no existen

<!-- gvc-ddd-decision: q13 -->
Status: accepted

Sección de origen: §4, §5.10

## Contexto

gmod y grun están vacíos y el GVE aún no mide narración, pero forge tiene que poder desarrollarse.

## Decisión

forge define puertos (`MachinePort`, `QueuePort`, `MeasurePort`) que fallan cerrados con el motivo y no implementa nada de esos repos (invariante 10).

## Consecuencias

Sin el repo, la operación falla con el motivo y la orden o el repo que falta; nunca se finge una medida ni un cerrojo.

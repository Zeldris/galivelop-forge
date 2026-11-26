# El modelo base se elige solo vía gmod

<!-- gvc-ddd-decision: q6 -->
Status: accepted

Sección de origen: §3

## Contexto

Había que decidir si usar Model Atlas directamente o a través de gmod.

## Decisión

Solo vía gmod (`MachinePort`). Model Atlas, si existe, será una entrada del catálogo de gmod.

## Consecuencias

forge no consulta catálogos por su cuenta. Hoy gmod está vacío, así que el puerto falla cerrado (ADR 0013).

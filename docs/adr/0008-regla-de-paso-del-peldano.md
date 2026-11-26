# Un peldaño pasa con la demostración del GVE y un mínimo opcional

<!-- gvc-ddd-decision: q8 -->
Status: accepted

Sección de origen: §2, §5.4

## Contexto

Había que fijar cuándo se da por bueno un peldaño.

## Decisión

Pasa cuando la `gve.comparison/1` frente a la línea base dice `demonstrated` (regla de demostración del GVE) y, si el objetivo lo fija, se supera su mínimo absoluto (`Threshold`).

## Consecuencias

El umbral deja de ser la regla única y pasa a ser un mínimo absoluto opcional. forge no mide por su cuenta.

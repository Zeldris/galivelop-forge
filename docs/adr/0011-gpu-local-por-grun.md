# Todo uso de la GPU local pasa por el cerrojo de grun

<!-- gvc-ddd-decision: q11 -->
Status: accepted

Sección de origen: §3, §5.6

## Contexto

Hay que evitar que forge compita por la GPU de una máquina Galivelop.

## Decisión

Todo lo que use la GPU de una máquina Galivelop (medir, servir, entrenar en GPU propia) pasa por el cerrojo de grun. Lo remoto no, pero la receta lo declara.

## Consecuencias

`train` local sin grun disponible falla cerrado; una receta remota sin motivo no valida (invariante 6).

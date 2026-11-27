# Roadmap de galivelop-forge

Los hitos de `docs/ddd.md` §7 repartidos en versiones semver. Cada tarea tiene un id (`<versión>-<n>`) para los
commits y un estado: `hecho`, `en curso`, `pendiente` o `bloqueado (<por qué>)`. Una versión se cierra cuando todas
sus tareas están hechas y se cumple su «Pasa si».

| Versión | Hito | Pasa si | Depende de | Estado |
|---|---|---|---|---|
| 0.0.1 | F-1 + F0 | DDD borrador 2, ADR 0001-0013, reglas y roadmap en `main`. | — | hecho |
| 0.1.0 | F1 Datos | Un export real de Tarkor entra como `gforge.dataset/0` válido en gart, con las invariantes 1, 2, 3, 7, 9 y 10 con su test. | gart (alta de `gforge`) | pendiente |
| 0.2.0 | F2 Línea base | Hay una `gve.evidence/1` válida del narrador para el modelo actual y para el candidato pequeño. | GVE 0.3, gmod | bloqueado (GVE 0.3, gmod) |
| 0.3.0 | F3 Peldaño 1 | Prompt y Modelfile del narrador tienen su `gve.comparison/1` y `next_rung` decide con ella. | 0.2.0, grun | bloqueado (0.2.0, grun) |
| 0.4.0 | F4 Peldaño 2 | Un SFT con LoRA/QLoRA hecho fuera de la Deck da un GGUF que corre en la Deck y tiene su medida. | 0.3.0 | bloqueado (0.3.0) |
| 0.5.0 | F5 Publicación | El primer modelo que pasa se publica solo en Hugging Face con su `gforge.card/0`. | 0.4.0, credencial de HF | bloqueado (0.4.0) |
| 0.6.0 | F6 Peldaño 3 | Un DPO del narrador tiene su medida, y un segundo objetivo de otra aplicación entra con su adaptador. | 0.5.0 | bloqueado (0.5.0) |
| 1.0.0 | Estable | Se cumplen los criterios de éxito 1-4 del DDD §1 y los artefactos `gforge.*` pasan de `/0` a `/1`. | 0.6.0 | bloqueado (0.6.0) |

## 0.0.1: diseño (F-1 + F0)

- 0.0.1-1 DDD borrador 2 con las decisiones q1-q13. `hecho`
- 0.0.1-2 ADR 0001-0013. `hecho`
- 0.0.1-3 `AGENTS.md`, `REVIEW.md` y `GLOSSARY.md` al día con los ADR. `hecho`
- 0.0.1-4 Este roadmap. `hecho`
- 0.0.1-5 Revisión del bloque, retro y subida a `main` con la confirmación de la persona. `hecho`

## 0.1.0: datos (F1)

- 0.1.0-1 Paquete `gforge` (stdlib), puertos vacíos que fallan cerrados (invariante 10) y test de importación limpia (invariante 7). `hecho`
- 0.1.0-2 Vendorizar gart con su test de huella sha256; alta del espacio `gforge` en gart. `bloqueada`: gart aún sin código; aviso en [`records/aviso-gart.md`](records/aviso-gart.md).
- 0.1.0-3 Esquema `gforge.dataset/0` y su validación. `bloqueada` (espera a 0.1.0-2).
- 0.1.0-4 Fuente Tarkor: leer los exports de destilación y DPO (sin ejecutar los scripts del juego). `hecho`: `gforge.sources.tarkor`, formato en [`sources/tarkor.md`](sources/tarkor.md); falta probarlo con un export real (lo genera la persona).
- 0.1.0-5 Filtros de datos personales (invariante 2) y de maestro (invariante 9, lista de maestros abiertos). `hecho`: `gforge.filters` y `gforge.teachers`; la lista de maestros, a falta de que la persona la confirme (Q-6).
- 0.1.0-6 Particiones deterministas por semilla y hash (invariante 3); `test` como lote de reserva del GVE.
- 0.1.0-7 La licencia viaja (invariante 1) y `datasets/<objetivo>/<versión>/` en el repo.

## 0.2.0 en adelante

Las tareas se detallan al abrir cada versión, con los DDD de gmod y grun y la versión 0.3 del GVE ya disponibles. Lo
que no se puede probar con tests aquí (la Deck, una GPU alquilada) se apunta como pendiente, con quién lo comprueba y
dónde.

Avisos que hay que dar a los repos hermanos (a cargo de la persona o de una sesión en ese repo; desde aquí no se
modifican):
- gart: alta del espacio `gforge`.
- gmod/grun: lo que forge espera de `MachinePort` y `QueuePort`.
- GVE: forge va a consumir `gve.evidence/1` y `gve.comparison/1` del narrador.

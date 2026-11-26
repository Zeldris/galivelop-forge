# DDD: galivelop-forge (borrador 2, 2026-11-26)

**Uso:** fábrica de datos y ajuste fino de los modelos locales de Galivelop ("escalera de mejora").
**Nombre / paquete / espacio:** `galivelop-forge` · paquete `gforge` · artefactos `gforge.*` (espacio por dar de alta
en gart).
**Visibilidad / stack:** público; Python 3.8+, el núcleo solo con la biblioteca estándar; los entrenadores son extras
opcionales.
**Licencia:** MIT para el código; CC BY-NC-SA 4.0 para el contenido, datasets incluidos (q2).
**Depende de:** `galivelop-artifacts` (gart, vendorizado), `galivelop-models` (gmod: máquina y catálogo),
`galivelop-runtime` (grun: cola, cerrojo de GPU) y `galivelop-evaluator` (GVE: las medidas). gmod y grun aún no
existen más allá del repo vacío, y el GVE aún no mide narración: forge habla con todos a través de puertos que fallan
cerrados (q13).

**Cambios frente al borrador 1:** cerradas las seis preguntas de §8 y siete más que salieron al contrastar con gart,
GVE y galivelop-developer (tabla «Decisiones de la F-1»). Los peldaños empiezan en el prompt (q9); el umbral pasa a
ser la regla de demostración del GVE más un mínimo opcional (q8); `Run` pasa a `Entrenamiento` (q12); nueva
invariante de procedencia del maestro (q7); la Deck solo infiere (q3); los datasets viven en el repo (q2) y la
publicación en Hugging Face es automática con medida en verde (q4).

## 1. Propósito

Unir en una sola herramienta la escalera de correcciones del GVE (sus peldaños de prompt, Modelfile y pesos) y la
escalera por modelo que investigó galivelop-developer. Coge datos de las aplicaciones (primero Tarkor), los convierte
en datasets versionados y con licencia, pide al GVE la línea base y sube peldaños de ajuste (prompt → Modelfile →
SFT con LoRA → DPO) solo cuando el peldaño de abajo no pasa. Lo que mejora se publica con su ficha y sus medidas.

Criterios de éxito:
1. El narrador de Tarkor, ajustado sobre un modelo que corre en la Steam Deck, pasa la regla de demostración del GVE
   contra el modelo de origen en la misma batería. *Depende de la medida de narración del GVE (su versión 0.3, q10).*
2. Cada modelo publicado se puede reproducir: dataset (hash), receta, semilla, versión del entrenador y medidas
   enlazadas.
3. Ningún peldaño se sube sin la medida que lo justifica.
4. Un dataset nuevo de otra aplicación entra con un adaptador, sin tocar el núcleo.

## 2. Lenguaje

| Término | Código | Significado |
|---|---|---|
| Fuente | `Source` | Adaptador que lee lo que exporta una aplicación (p. ej. los scripts de dataset de Tarkor). |
| Ejemplo | `Example` | Una pareja entrada→salida (SFT) o entrada→elegida/rechazada (DPO), con procedencia y maestro. |
| Maestro | `Teacher` | Modelo que generó la salida de un ejemplo; tiene que ser abierto y permitir entrenar con sus salidas (q7). |
| Dataset | `Dataset` | Conjunto versionado de ejemplos, con licencia, procedencia, hash y particiones; vive en `datasets/` (q2). |
| Partición | `Split` | train / val / test, decidida por la semilla y el hash del ejemplo, nunca al azar. `test` es el equivalente del «lote de reserva» del GVE: nunca lo ve el entrenamiento. |
| Peldaño | `Rung` | Nivel de ajuste: `prompt`, `modelfile`, `sft`, `dpo` (q9). |
| Receta | `Recipe` | Qué peldaño, sobre qué modelo base y dataset, con qué método (`lora`, `qlora`), hiperparámetros, semilla y máquina. |
| Entrenamiento | `TrainingRun` | Ejecución de una receta: estado, máquina, duración, pesos producidos (q12). No confundir con la «corrida» del GVE ni con `gdev.run/0`. |
| Medida | `Measure` | Lo que forge recibe del GVE: una `gve.evidence/1` válida y, frente a otra, una `gve.comparison/1`. |
| Línea base | `Baseline` | Medida del GVE del modelo sin ajustar, con el sistema de la aplicación ya puesto (RAG, verificador). |
| Umbral | `Threshold` | Mínimo absoluto opcional del objetivo, además de la regla de demostración del GVE (q8). |
| Escalera | `Ladder` | Secuencia de peldaños de un objetivo, con la medida de cada uno. |
| Ficha | `Card` | Model card publicable: origen, dataset, maestro, licencia, medidas y límites. |
| Objetivo | `Target` | Tarea concreta que se quiere mejorar (p. ej. `tarkor.narrator`). |
| Puerto | `Port` | Interfaz de forge hacia otro repo (`MachinePort`, `QueuePort`, `MeasurePort`, `TrainerPort`, `PublishPort`); sin el repo, falla cerrado (q13). |

## 3. Contextos acotados

1. **Fuentes:** adaptadores por aplicación. El primero es Tarkor: `generate-distillation-dataset.ts`,
   `generate-dpo-dataset.ts`, `export-dpo-dataset.ts`, `split-distillation-dataset.ts` y `generar-dataset-dpo.sh`.
   forge lee lo que esos scripts exportan y no los ejecuta dentro del repo del juego.
2. **Dataset:** normaliza, quita duplicados, filtra datos personales y maestros no permitidos, particiona y versiona.
   Es el corazón determinista y vive en el repo (`datasets/<objetivo>/<versión>/`).
3. **Medida:** pide al GVE la línea base y la medida de cada entrenamiento (`MeasurePort`); nunca mide por su cuenta.
4. **Escalera de ajuste:** decide el siguiente peldaño según las medidas y lanza la receta.
5. **Entrenamiento:** ejecuta la receta con el entrenador opcional (`TrainerPort`). En una máquina Galivelop pasa por
   la cola y el cerrojo de grun; en una máquina alquilada (Colab u otra) lo declara la receta (q3, q11).
6. **Publicación:** genera la ficha y, con medida en verde, publica en Hugging Face sin intervención (q4).

Mapa con los demás repos:
- **gart:** valida todos los artefactos `gforge.*`. Se vendoriza como copia con versión y test de huella sha256
  (ADR 0002 de gart). Cada artefacto declara su tipo en el campo `schema` con un KindId `<espacio>.<nombre>/<n>`;
  `/0` es provisional y nunca se publica como estable. El espacio `gforge` se da de alta en gart (solo su dueño
  publica en él).
- **gmod:** dice qué modelos base caben en la máquina y recibe los modelos nuevos en su catálogo. forge elige el
  modelo base solo a través de gmod (q6). Hoy gmod está vacío; el perfil de máquina y el catálogo por rol y nivel
  viven en galivelop-developer (`machine-profile.json`, `gdev.catalog/0`) y se espera que pasen a gmod.
- **grun:** cola y cerrojo de GPU de cada máquina Galivelop; forge es un cliente más. Hoy grun está vacío. La
  planificación entre aplicaciones es suya o de un repo futuro, no de forge (q1, provisional hasta el DDD de grun).
- **GVE:** aporta la batería y el veredicto; forge le pasa el modelo y recibe `gve.evidence/1` y `gve.comparison/1`.
  Hoy el GVE mide recuperación RAG (recall@k, MRR@k); la medida de narración es su versión 0.3 (q10).
- **galivelop-developer:** su investigación de mejora por modelo (2026-11-21) es el origen de la escalera de forge y
  de las reglas q3 y q7; forge la ejecuta. Su `bench/ladder` (escalera de tareas `gdev.task/0`) es otra cosa.
- **Tarkor (WMF):** solo fuente de datos y primer consumidor de los modelos; desde aquí no se modifica.

## 4. Modelo

- **Agregado `Ladder`** (raíz) por objetivo: su `Baseline`, sus peldaños en orden, la `Recipe` y el `TrainingRun` de
  cada peldaño, la medida de cada uno y el estado (`open`, `passed`, `exhausted`).
- **Entidades:** `Dataset` (id + versión), `Recipe`, `TrainingRun`, `Card`.
- **Objetos de valor:** `Example`, `Teacher`, `Split`, `Rung`, `Threshold`, `Licence` (SPDX + condiciones),
  `Provenance` (fuente, commit, fecha, maestro), `DatasetHash`, `Seed`, `Machine` (`local:<perfil>` o `rented` con
  motivo).
- **Puertos** (q13): `MachinePort` (gmod), `QueuePort` (grun), `MeasurePort` (GVE), `TrainerPort` (extra
  opcional), `PublishPort` (Hugging Face). Sin su implementación, cada operación falla con el motivo y la orden o el
  repo que falta.
- **Servicios:**
  - `ingest(source) → Dataset`
  - `split(dataset, seed) → Split`
  - `baseline(target, model) → Measure` (vía `MeasurePort`)
  - `next_rung(ladder) → Rung | None`
  - `train(recipe) → TrainingRun` (vía `TrainerPort`; con máquina local, dentro del cerrojo de `QueuePort`)
  - `card(training) → Card`
  - `publish(card)` (vía `PublishPort`, automática con medida en verde)
- **Eventos:** `DatasetBuilt`, `BaselineMeasured`, `RungStarted`, `TrainingFinished`, `RungPassed`, `RungFailed`,
  `LadderExhausted`, `CardReady`, `Published`.
- **Artefactos gart** (todos `/0`, provisionales):
  - `gforge.dataset/0`: manifiesto del dataset (ejemplos por hash, licencia, procedencia, maestros, particiones).
  - `gforge.recipe/0`: receta de un peldaño.
  - `gforge.training/0`: resultado de un entrenamiento, con la medida del GVE enlazada.
  - `gforge.card/0`: ficha publicable (incluye las medidas en el formato `.eval_results` de Hugging Face).

## 5. Invariantes

1. **La licencia viaja:** un modelo hereda la licencia más restrictiva de sus datasets (CC BY-NC-SA de Tarkor
   incluida). *Test:* una receta con un dataset NC produce una ficha con NC; una ficha sin licencia no valida.
2. **Sin datos personales:** el ingest rechaza el ejemplo que casa con los filtros (correos, teléfonos, nombres
   reales de la lista). *Test:* un ejemplo con correo se rechaza y se nombra el motivo.
3. **Particiones deterministas:** la misma semilla y los mismos ejemplos dan siempre la misma partición, y ningún
   ejemplo de test aparece en train. *Test:* dos ejecuciones dan particiones idénticas; la intersección es vacía.
4. **Sin publicar sin medida:** `publish` exige un `gforge.training/0` con una `gve.evidence/1` válida (sin
   `dirty`, con los hashes que el GVE pide) y una `gve.comparison/1` con veredicto `demonstrated` frente a la línea
   base, y el mínimo del umbral si el objetivo lo tiene. *Test:* un entrenamiento sin medida, con evidencia no
   válida o sin demostrar se rechaza con el motivo.
5. **Un peldaño necesita su medida:** no se sube de peldaño sin la medida del de abajo, y solo si no pasó. *Test:*
   `next_rung` sin medida previa falla; con el peldaño de abajo aprobado devuelve `None`.
6. **La GPU local pasa por grun:** ningún entrenamiento ni medida toma la GPU de una máquina Galivelop fuera del
   cerrojo de grun; uno remoto lleva `machine: rented` y su motivo. *Test:* `train` local sin grun disponible falla
   cerrado; una receta remota sin motivo no valida.
7. **Núcleo stdlib:** el núcleo importa sin los extras; sin entrenador instalado, `train` falla con la orden que
   lo instala. *Test:* importar `gforge` en un entorno limpio; el mensaje de `train` nombra el extra.
8. **Reproducible:** un `TrainingRun` guarda el hash del dataset, la receta, la semilla y la versión del
   entrenador. *Test:* un entrenamiento sin cualquiera de esos campos no valida en gart.
9. **Solo maestros abiertos** (q7): cada ejemplo generado por un modelo nombra a su maestro, y el ingest rechaza los
   de un maestro cuyos términos prohíben entrenar con sus salidas (Claude, GPT…) o sin maestro declarado. *Test:* un
   ejemplo con maestro `claude-*` o sin maestro se rechaza con el motivo; uno con un maestro de la lista abierta pasa.
10. **Puertos que fallan cerrados** (q13): sin gmod, grun o el GVE, la operación que los necesita falla con el motivo;
    nunca se finge una medida ni un cerrojo. *Test:* `baseline` sin `MeasurePort` falla y nombra el repo.

## 6. Alcance

**Dentro:** adaptadores de fuente; formato, versionado y almacenamiento de datasets en el repo; particiones; escalera
de peldaños desde el prompt; recetas; entrenamientos locales vía grun o remotos declarados; enlace con las medidas del
GVE; fichas y publicación automática en Hugging Face.

**Fuera:**
- medir (es del GVE);
- servir modelos, la cola y la planificación entre aplicaciones (grun o un repo futuro, q1);
- el catálogo y el perfil de máquina (gmod);
- el sistema alrededor del modelo: RAG, salidas estructuradas y verificador (son de la aplicación; la línea base se
  mide con ellos puestos, q9);
- generar los datos dentro de la aplicación (los scripts de Tarkor siguen en su repo);
- entrenar en la Steam Deck (q3) y entrenar modelos desde cero.

## 7. Escalera de hitos

| Hito | Nivel | Qué | Lo decide | Depende de |
|---|---|---|---|---|
| F-1 | Diseño | Este borrador 2: contraste con los repos hermanos y decisiones q1-q13. | Usuario | — |
| F0 | Diseño | Decisiones a `main` como ADR, glosario, reglas del proyecto al día y reparto de los hitos en versiones. | Usuario | F-1 |
| F1 | Datos | `gforge.dataset/0`, ingest del export de Tarkor (destilación y DPO), particiones, filtros de datos personales y de maestro, `datasets/` en el repo; alta de `gforge` en gart. | Tests | — |
| F2 | Línea base | Medida del narrador con el GVE sobre el modelo actual y el candidato pequeño. | GVE | GVE 0.3, gmod |
| F3 | Peldaño 1 | Prompt y Modelfile del narrador medidos contra la línea base. | GVE + umbral | F2, grun |
| F4 | Peldaño 2 | SFT con LoRA/QLoRA del narrador (Unsloth, fuera de la Deck) y exportación a GGUF para Ollama. | GVE + umbral | F3 |
| F5 | Publicación | Ficha `gforge.card/0` y publicación automática en Hugging Face del primer modelo que pase. | Invariante 4 | F4 |
| F6 | Peldaño 3 | DPO con las parejas de Tarkor; segundo objetivo de otra aplicación. | GVE + usuario | F5 |

F1 no depende de ningún repo hermano salvo gart (q10); F2 en adelante esperan al GVE 0.3 y a gmod/grun.

## 8. Preguntas abiertas

_(ninguna: todas cerradas en la F-1, ver la tabla de abajo. Lo que queda provisional es q1, hasta el DDD de grun.)_

## Decisiones de la F-1

| id | Pregunta | Respuesta | Sección |
|---|---|---|---|
| q1 | ¿La planificación entre aplicaciones es de forge? | No: forge es un cliente más de la cola de grun; las prioridades entre aplicaciones son de grun o de un repo futuro. Provisional: se revisa cuando grun tenga DDD. | §3, §6 |
| q2 | ¿Dónde viven los datasets de Tarkor (CC BY-NC-SA)? | En el repo de forge (`datasets/`), bajo la licencia de contenido CC BY-NC-SA 4.0, la misma que Tarkor; sin servicio externo para los datos. Git LFS solo si un archivo pasa del umbral del flujo. | §3, §6 |
| q3 | ¿Dónde se entrena? | La Steam Deck solo infiere (prompt, Modelfile, medida). LoRA/SFT/DPO en una GPU propia o alquilada (Colab), con la máquina y el motivo en la receta; el resultado tiene que correr en la Deck. | §3, §5.6 |
| q4 | ¿Publicación en Hugging Face a mano o automática? | Automática, cuando el entrenamiento cumple la invariante 4. Sin credencial de Hugging Face, `publish` falla cerrado. | §3, §5.4 |
| q5 | ¿Qué entrenador? | Interfaz `TrainerPort` en el núcleo; primer extra Unsloth (LoRA/QLoRA para SFT y DPO) con exportación a GGUF y Modelfile para Ollama (con `ADAPTER` sobre el mismo modelo base exacto, o pesos fusionados). Los demás, cuando haga falta. | §4 |
| q6 | ¿Model Atlas directo o vía gmod? | Solo vía gmod (`MachinePort`); Model Atlas, si existe, será una entrada del catálogo de gmod. | §3 |
| q7 | ¿Se aceptan salidas de modelos cerrados como datos? | No: solo maestros abiertos cuyos términos permiten entrenar con sus salidas; cada ejemplo nombra a su maestro (invariante 9). Sigue la decisión de galivelop-developer. | §2, §5.9 |
| q8 | ¿Cuándo pasa un peldaño? | Cuando la `gve.comparison/1` frente a la línea base dice `demonstrated` (regla de demostración del GVE) y, si el objetivo lo fija, se supera su mínimo absoluto (`Threshold`). | §2, §5.4 |
| q9 | ¿Qué peldaños tiene la escalera? | `prompt` → `modelfile` → `sft` (LoRA/QLoRA) → `dpo`. RAG, salidas estructuradas y verificador son del sistema de la aplicación; la línea base se mide con ellos puestos. | §2, §6 |
| q10 | ¿Qué pasa mientras el GVE no mide narración? | F1 arranca ya; F2 en adelante quedan bloqueados por la versión 0.3 del GVE. forge nunca mide por su cuenta. | §7 |
| q11 | ¿Qué papel tiene grun en el entrenamiento? | Todo lo que use la GPU de una máquina Galivelop (medir, servir, entrenar en GPU propia) pasa por su cerrojo; lo remoto no, pero la receta lo declara. | §3, §5.6 |
| q12 | ¿Cómo se llama la ejecución de una receta? | `Entrenamiento` (`TrainingRun`, `gforge.training/0`); «corrida» queda para el GVE y `gdev.run/0` para developer. | §2, §4 |
| q13 | ¿Qué hace forge mientras gmod y grun no existen? | Define puertos (`MachinePort`, `QueuePort`, `MeasurePort`) que fallan cerrados con el motivo; no implementa nada de esos repos (invariante 10). | §4, §5.10 |

## Pendiente para F0

- ~~Llevar q1-q13 a `docs/adr/NNNN-<slug>.md` (formato del flujo: `.claude/skills/domain-modeling/ADR-FORMAT.md`).~~ — hecho: docs/adr/0001-0013
- Poner al día `AGENTS.md`, `REVIEW.md` y `GLOSSARY.md` con q2 (datos NC en el repo) y q4 (publicación automática).
- Repartir F1-F6 en versiones (`0.1.0`…), con tareas con id y estado, al estilo del roadmap del GVE.
- Avisar a gart (alta del espacio `gforge`), a gmod/grun (lo que forge espera de sus puertos) y al GVE (que forge
  consumirá `gve.evidence/1` y `gve.comparison/1` del narrador).

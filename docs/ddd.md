# DDD: galivelop-forge (borrador 1, 2026-11-26)

**Uso:** fábrica de datos y ajuste fino de los modelos locales de Galivelop ("escalera de mejora").
**Nombre / paquete / espacio:** `galivelop-forge` · paquete `gforge` · artefactos `gforge.*`
**Visibilidad / stack:** público; Python 3, el núcleo solo con la biblioteca estándar; los entrenadores son extras opcionales.
**Depende de:** `galivelop-artifacts` (gart, vendorizado), `galivelop-models` (gmod: máquina y catálogo),
`galivelop-runtime` (grun: cola, cerrojo de GPU) y `galivelop-evaluator` (GVE: las medidas).

## 1. Propósito

Unir en una sola herramienta la escalera de arreglos del GVE y la escalera por modelo de galivelop-developer.
Coge datos de las aplicaciones (primero Tarkor), los convierte en datasets versionados y con licencia, mide el
modelo base con el GVE y sube peldaños de ajuste (Modelfile → LoRA → SFT/DPO) solo cuando el peldaño de abajo no
llega al umbral. Lo que mejora se publica con su ficha y sus medidas.

Criterios de éxito:
1. El narrador de Tarkor destilado a un modelo más pequeño iguala o supera la nota del GVE del modelo de origen,
   en la misma batería, y corre en la Steam Deck.
2. Cada modelo publicado se puede reproducir: dataset (hash), receta, semilla y medidas enlazadas.
3. Ningún peldaño se sube sin la medida que lo justifica.
4. Un dataset nuevo de otra aplicación entra con un adaptador, sin tocar el núcleo.

## 2. Lenguaje

| Término | Código | Significado |
|---|---|---|
| Fuente | `Source` | Adaptador que lee los datos crudos de una aplicación (p. ej. los scripts de dataset de Tarkor). |
| Ejemplo | `Example` | Una pareja entrada→salida (SFT) o entrada→elegida/rechazada (DPO), con procedencia. |
| Dataset | `Dataset` | Conjunto versionado de ejemplos, con licencia, procedencia, hash y particiones. |
| Partición | `Split` | train / val / test, decidida por la semilla y el hash del ejemplo, nunca al azar. |
| Peldaño | `Rung` | Nivel de ajuste: `modelfile`, `lora`, `sft`, `dpo`. |
| Receta | `Recipe` | Qué peldaño, sobre qué modelo base y dataset, con qué hiperparámetros y semilla. |
| Corrida | `Run` | Ejecución de una receta: estado, máquina, duración, pesos producidos. |
| Línea base | `Baseline` | Medida del GVE del modelo sin ajustar, la que hay que superar. |
| Umbral | `Threshold` | Nota mínima del GVE que da por bueno un peldaño. |
| Escalera | `Ladder` | Secuencia de peldaños de un objetivo, con la medida de cada uno. |
| Ficha | `Card` | Model card publicable: origen, dataset, licencia, medidas y límites. |
| Objetivo | `Target` | Tarea concreta que se quiere mejorar (p. ej. `tarkor.narrator`). |

## 3. Contextos acotados

1. **Fuentes:** adaptadores por aplicación. El primero es Tarkor: `generate-distillation-dataset.ts`,
   `generate-dpo-dataset.ts`, `export-dpo-dataset.ts`, `split-distillation-dataset.ts` y `generar-dataset-dpo.sh`.
   forge lee lo que esos scripts exportan y no los ejecuta dentro del repo del juego.
2. **Dataset:** normaliza, quita duplicados, filtra datos personales, particiona y versiona. Es el corazón determinista.
3. **Medida:** pide al GVE la línea base y la medida de cada corrida; nunca mide por su cuenta.
4. **Escalera de ajuste:** decide el siguiente peldaño según las medidas y lanza la receta.
5. **Entrenamiento:** ejecuta la corrida como trabajo de grun (cerrojo de GPU) con el entrenador opcional instalado.
6. **Publicación:** genera la ficha y, solo con medida en verde, prepara la subida a Hugging Face.

Mapa con los demás repos:
- **gart:** valida todos los artefactos `gforge.*`.
- **gmod:** dice qué modelos base caben en la máquina (`gmod.machine/0`) y recibe los modelos nuevos en su catálogo.
- **grun:** ejecuta las corridas y los turnos de Ollama; forge es un cliente más de su cola.
- **GVE:** aporta la batería y la nota; forge le pasa el modelo y recibe `gve.*`.
- **galivelop-developer:** su escalera por modelo pasa a ser un `Ladder` de forge (forge es la que la ejecuta).
- **Tarkor (WMF):** solo fuente de datos y primer consumidor de los modelos; desde aquí no se modifica.

## 4. Modelo

- **Agregado `Ladder`** (raíz) por objetivo: su `Baseline`, sus peldaños en orden, la `Recipe` y la `Run` de cada
  peldaño, la medida de cada uno y el estado (`open`, `passed`, `exhausted`).
- **Entidades:** `Dataset` (id + versión), `Recipe`, `Run`, `Card`.
- **Objetos de valor:** `Example`, `Split`, `Rung`, `Threshold`, `Licence` (SPDX + condiciones), `Provenance`
  (fuente, commit, fecha), `DatasetHash`, `Seed`.
- **Servicios:**
  - `ingest(source) → Dataset`
  - `split(dataset, seed) → Split`
  - `baseline(target, model) → Measure` (vía GVE)
  - `next_rung(ladder) → Rung | None`
  - `train(recipe) → Run` (vía grun)
  - `card(run) → Card`
  - `publish(card)` (preparado; ver §8)
- **Eventos:** `DatasetBuilt`, `BaselineMeasured`, `RungStarted`, `RunFinished`, `RungPassed`, `RungFailed`,
  `LadderExhausted`, `CardReady`.
- **Artefactos gart:**
  - `gforge.dataset/0`: manifiesto del dataset (ejemplos por hash, licencia, procedencia, particiones).
  - `gforge.recipe/0`: receta de un peldaño.
  - `gforge.run/0`: resultado de una corrida, con la medida del GVE enlazada.
  - `gforge.card/0`: ficha publicable.

## 5. Invariantes

1. **La licencia viaja:** un modelo hereda la licencia más restrictiva de sus datasets (CC BY-NC-SA de Tarkor
   incluida). *Test:* una receta con un dataset NC produce una ficha con NC; una ficha sin licencia no valida.
2. **Sin datos personales:** el ingest rechaza el ejemplo que casa con los filtros (correos, teléfonos, nombres
   reales de la lista). *Test:* un ejemplo con correo se rechaza y se nombra el motivo.
3. **Particiones deterministas:** la misma semilla y los mismos ejemplos dan siempre la misma partición, y ningún
   ejemplo de test aparece en train. *Test:* dos ejecuciones dan particiones idénticas; la intersección es vacía.
4. **Sin publicar sin medida:** `publish` exige una `gforge.run/0` con medida del GVE por encima del umbral y de la
   línea base. *Test:* una corrida sin medida o por debajo se rechaza con el motivo.
5. **Un peldaño necesita su medida:** no se sube de peldaño sin la medida del de abajo, por debajo del umbral.
   *Test:* `next_rung` sin medida previa falla; con el umbral superado devuelve `None`.
6. **El entrenamiento pasa por grun:** ninguna corrida toma la GPU fuera del cerrojo. *Test:* `train` sin grun
   disponible falla cerrado.
7. **Núcleo stdlib:** el núcleo importa sin los extras; sin entrenador instalado, `train` falla con la orden que
   lo instala. *Test:* importar `gforge` en un entorno limpio; el mensaje de `train` nombra el extra.
8. **Reproducible:** una `Run` guarda el hash del dataset, la receta, la semilla y la versión del entrenador.
   *Test:* una run sin cualquiera de esos campos no valida en gart.

## 6. Alcance

**Dentro:** adaptadores de fuente, formato y versionado de datasets, particiones, escalera de peldaños, recetas,
corridas vía grun, enlace con las medidas del GVE, fichas y preparación de la publicación.

**Fuera:**
- medir (es del GVE);
- servir modelos y la cola (grun);
- el catálogo y el perfil de máquina (gmod);
- generar los datos dentro de la aplicación (los scripts de Tarkor siguen en su repo);
- la planificación entre aplicaciones con prioridades globales (ver §8.1);
- entrenar modelos desde cero.

## 7. Escalera de hitos

| Hito | Nivel | Qué | Lo decide |
|---|---|---|---|
| F0 | Diseño | Este DDD, glosario, ADR de licencias y de entrenadores opcionales. | Usuario |
| F1 | Datos | `gforge.dataset/0`, ingest del export de Tarkor (destilación y DPO), particiones y filtro de datos personales. | Tests |
| F2 | Línea base | Medida del narrador con el GVE sobre el modelo actual y el candidato pequeño. | GVE |
| F3 | Peldaño 1 | Modelfile del narrador (prompt de sistema y parámetros) medido contra la línea base. | GVE + umbral |
| F4 | Peldaño 2 | LoRA o destilación SFT del narrador, en la Deck o fuera (§8.3), vía grun. | GVE + umbral |
| F5 | Publicación | Ficha `gforge.card/0` y subida a Hugging Face del primer modelo que pase. | Usuario |
| F6 | Peldaño 3 | DPO con las parejas de Tarkor; segundo objetivo de otra aplicación. | GVE + usuario |

## 8. Preguntas abiertas

1. **La planificación entre aplicaciones** (el DDD de grun la nombraba "futuro: forge orquesta pedidos de varias
   aplicaciones"): ¿se queda fuera de forge? Choca con forge como fábrica de datos.
   **Recomendación:** sí, fuera. Va a grun (prioridades en su cola) o a un repo futuro, y en el DDD de grun se
   corrige la mención.
2. **Dónde viven los datasets de Tarkor**, por su licencia CC BY-NC-SA: ¿en forge, en el repo del juego o en
   Hugging Face?
   **Recomendación:** fuera del repo de forge. forge guarda solo el manifiesto (`gforge.dataset/0` con hashes) y
   los datos se publican en Hugging Face con su misma licencia NC; el repo queda con su licencia abierta.
3. **Dónde se entrena:** la Deck es la máquina mínima, pero un LoRA o un SFT puede no caber o tardar días.
   **Recomendación:** Modelfile y LoRA pequeño en la Deck (máquina mínima). Una GPU alquilada solo como excepción
   apuntada en la receta (`machine: rented`, con el motivo), como manda "IA local primero".
4. **Publicación en Hugging Face:** ¿a mano o automática?
   **Recomendación:** forge lo deja todo preparado (ficha, archivos, orden) y la subida la confirma el usuario;
   nada se publica solo.
5. **El entrenador:** ¿cuál es el extra opcional: unsloth, `llama.cpp` finetune, PEFT/TRL?
   **Recomendación:** una interfaz `Trainer` con un primer adaptador para unsloth (LoRA en GPU pequeña) y la
   exportación a GGUF para Ollama; los demás, cuando haga falta.
6. **Model Atlas:** ¿forge lo usa directamente o solo a través de gmod?
   **Recomendación:** solo a través de gmod. Model Atlas es una entrada del catálogo de gmod y forge elige el
   modelo base preguntando a gmod.

## Decisiones

_(ninguna aún: pendientes de §8)_

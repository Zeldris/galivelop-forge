# Fuente Tarkor: qué leemos y cómo

Lo que `gforge.sources.tarkor` lee de lo que exportan los scripts de dataset de Tarkor (repo
`Zeldris/World-Maker-Fantasy`, leído en `cad662d`, solo lectura; las rutas son de `backend/`). forge lee lo
exportado y nunca ejecuta los scripts.

## Destilación (SFT)

- **Lo escribe** `src/scripts/generate-distillation-dataset.ts` en `output/distillation-dataset/<categoría>.jsonl`, un
  archivo por categoría, en modo append y reanudable por `id`.
- **Registro:** `{"id", "category", "provider", "messages": [system, user, assistant]}`.
  - `system` es el bloque SYSTEM de `Modelfile.llama31`.
  - `user` es el prompt de narración más el JSON Schema.
  - `assistant` es un `NarrationResult` serializado como cadena JSON (`narration: str` y `newFacts: str[]`
    obligatorios; el resto opcional, `src/services/narrador.ts`).
- **Maestro:** `provider` es el id del maestro en la nube (`gemini:…`, `groq:…`, `mistral:…`, `sambanova:…`,
  `cerebras:…`, `cloudflare:…`), y el filtro de 0.1.0-5 lo coteja con la lista de maestros abiertos (ADR 0007).
- **Datos personales:** ninguno; los escenarios están escritos a mano (`src/scripts/data/distillationScenarios.ts`).
- **Partición del juego:** `split-distillation-dataset.ts` deja `train.jsonl` y `eval.jsonl` en la misma carpeta,
  con una semilla que cambia con el número de líneas y sobre un orden de archivos sin ordenar. forge **las ignora** y
  parte por su cuenta (invariante 3).

## DPO

- **Lo escribe** `src/scripts/export-dpo-dataset.ts` en `output/dpo-dataset/live-dpo.jsonl`, en modo append. Lo saca de
  la tabla `LiveTeacherCapture`, que llenan las capturas del juego en vivo y el generador sintético
  `generate-dpo-dataset.ts` (lanzado por `generar-dataset-dpo.sh`).
- **Registro:** `{"id", "provider", "prompt": [system, user], "chosen": [assistant], "rejected": [assistant]}`.
  - `chosen` es el maestro.
  - `rejected` es el narrador local (`tarkor-narrador-llama31` por defecto; no viaja en el export).
- **Origen:**
  - Una pareja sintética lleva `<!-- scenario-id: <id> -->` al final del contenido de `user`. El lector lo quita, lo
    guarda en `scenario_id` y marca `origin = "synthetic"`.
  - Sin esa marca, la pareja es de una partida real (`origin = "live"`) y puede llevar texto escrito por el jugador
    y nombres de personaje: el filtro de datos personales (invariante 2) la trata aparte.
  - **La marca no es una garantía:** un jugador puede escribirla en su texto, así que `synthetic` no prueba que el
    contenido lo sea; no te fíes solo de ella para saltarte el filtro.
- **Faltan en el export** la categoría, el modelo local, `saveId`, `worldId` y `createdAt`.

## Qué hace el lector

- Lee los `<categoría>.jsonl` en orden de nombre, que es determinista, y `live-dpo.jsonl` en el orden del archivo.
- **Falla cerrado:** un JSON roto, un campo que falta, un rol equivocado, un `assistant` que no es un
  `NarrationResult`, una narración vacía, una categoría que no casa con su archivo o un `id` repetido paran la lectura con
  `SourceError` (archivo:línea y motivo). No se salta nada.
- La licencia (CC BY-NC-SA 4.0) no viaja en los exports: la pone forge (`gforge.datasets.build`, 0.1.0-7).

## Pendiente

- Validar el lector contra un export real, que el repo de Tarkor no tiene subido (`backend/output/` está en
  `.gitignore`). Lo genera la persona en su equipo; es el «Pasa si» de la 0.1.0.

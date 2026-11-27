# Questions

Questions for the user, one entry each; `python3 .claude/gw/scripts/questions.py` reads and rewrites this
file (format: header of scripts/questions.py). Answer by number: `questions.py answer "5. a, 6. ok"`.

## Q-1
- Refs: 0.1.0-2
- Status: answered
- Asked: 2026-11-26
- Question: gart todavía no tiene código (main en 2eca8da: solo documentación y flujo), así que no hay nada que vendorizar. ¿Cómo sigo? a) espero a gart sin avanzar; b) salto a 0.1.0-4..7 y dejo 0.1.0-2/3 bloqueadas; c) escribo en gforge un validador mínimo provisional de gforge.dataset/0 tras un puerto y lo cambio por gart cuando exista.
- Recommendation: b) Bloquear 0.1.0-2 y 0.1.0-3 hasta que gart publique código, y seguir ya con 0.1.0-4 a 0.1.0-7, que no dependen de gart; el dataset se valida al final con gart vendorizado.
- Answer: b
- Answered: 2026-11-27

## Q-2
- Refs: 0.1.0-2
- Status: answered
- Asked: 2026-11-26
- Question: ¿Redacto ya el aviso para gart (alta del espacio gforge y propuesta de la forma del test de huella sha256, que su ADR 0002 no define)?
- Recommendation: Sí: redacto en este repo (docs/records/aviso-gart.md) el aviso para gart: alta del espacio gforge, el KindId gforge.dataset/0, y una propuesta de cómo es el test de huella (qué bytes se hashean, dónde va el hash esperado y la versión), que ADR 0002 de gart no concreta. Lo llevas tú o una sesión en gart.
- Answer: ok
- Answered: 2026-11-27

## Q-3
- Refs: 0.1.0-2
- Status: answered
- Asked: 2026-11-26
- Question: gart no tiene archivo LICENSE (su ADR 0006 dice «la misma licencia que los demás repos Galivelop», sin fijarla). ¿Lo dejo como pendiente para gart en el aviso?
- Recommendation: Lo decide gart; aquí solo se apunta como pendiente en el aviso (sin licencia no se puede vendorizar ni declarar en THIRD-PARTY.md).
- Answer: ok
- Answered: 2026-11-27

## Q-4
- Refs: 0.1.0-4
- Status: answered
- Asked: 2026-11-27
- Question: Para 0.1.0-4 tengo que leer los exports de Tarkor, pero esta sesión no tiene su repo y el añadirlo (add_repo de Zeldris/Instalador-WMF-Tarkor) lo bloqueó el modo automático. ¿Cómo sigo? a) lo autorizas (o lo añades tú a la sesión) y lo leo con un subagente; b) me pasas un export de ejemplo (destilación y DPO) y trabajo sobre él; c) adelanto 0.1.0-5/6 sobre un registro genérico y dejo 0.1.0-4 bloqueada.
- Recommendation: a) Añadirlo solo para lectura: lo lee un subagente y devuelve un resumen con rutas y el formato de los exports; desde aquí no se modifica.
- Answer: a
- Answered: 2026-11-27

## Q-5
- Refs: 0.1.0-4
- Status: answered
- Asked: 2026-11-27
- Question: ¿Es Zeldris/Instalador-WMF-Tarkor el repo que tiene los scripts de dataset de Tarkor (es el único que encuentro con ese nombre)?
- Recommendation: Sí, si los scripts del DDD (generate-distillation-dataset.ts, generate-dpo-dataset.ts…) están en ese repo; si no, dime cuál es.
- Answer: World-Maker-Fantasy (Zeldris/World-Maker-Fantasy)
- Answered: 2026-11-27

## Q-6
- Refs: 0.1.0-5
- Status: answered
- Asked: 2026-11-27
- Question: La lista de maestros abiertos (gforge/teachers.py) decide qué ejemplos de Tarkor entran. ¿La confirmas? Propuesta: abiertos Llama 3.1+/Llama 4, DeepSeek-R1/V3 y gpt-oss; cerrados Claude, GPT, o1-o9 y Gemini (Gemini incluye todo lo de Tarkor con provider gemini:…); el resto (Qwen, Mistral, Gemma…) se rechaza hasta que alguien lo añada con su licencia. ¿O sigue otra lista ya decidida en galivelop-developer?
- Recommendation: a) Dejo la propuesta conservadora tal cual (Llama 3.1+/4, DeepSeek-R1/V3, gpt-oss abiertos; Claude, GPT, o1-o9 y Gemini cerrados; cualquier otro, rechazado) y tú me confirmas o añades familias. Si Tarkor genera sobre todo con gemini:…, esos ejemplos quedan fuera y conviene regenerarlos con un maestro abierto.
- Answer: a
- Answered: 2026-11-27

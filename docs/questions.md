# Questions

Questions for the user, one entry each; `python3 .claude/gw/scripts/questions.py` reads and rewrites this
file (format: header of scripts/questions.py). Answer by number: `questions.py answer "5. a, 6. ok"`.

## Q-1
- Refs: 0.1.0-2
- Status: open
- Asked: 2026-11-26
- Question: gart todavía no tiene código (main en 2eca8da: solo documentación y flujo), así que no hay nada que vendorizar. ¿Cómo sigo? a) espero a gart sin avanzar; b) salto a 0.1.0-4..7 y dejo 0.1.0-2/3 bloqueadas; c) escribo en gforge un validador mínimo provisional de gforge.dataset/0 tras un puerto y lo cambio por gart cuando exista.
- Recommendation: b) Bloquear 0.1.0-2 y 0.1.0-3 hasta que gart publique código, y seguir ya con 0.1.0-4 a 0.1.0-7, que no dependen de gart; el dataset se valida al final con gart vendorizado.

## Q-2
- Refs: 0.1.0-2
- Status: open
- Asked: 2026-11-26
- Question: ¿Redacto ya el aviso para gart (alta del espacio gforge y propuesta de la forma del test de huella sha256, que su ADR 0002 no define)?
- Recommendation: Sí: redacto en este repo (docs/records/aviso-gart.md) el aviso para gart: alta del espacio gforge, el KindId gforge.dataset/0, y una propuesta de cómo es el test de huella (qué bytes se hashean, dónde va el hash esperado y la versión), que ADR 0002 de gart no concreta. Lo llevas tú o una sesión en gart.

## Q-3
- Refs: 0.1.0-2
- Status: open
- Asked: 2026-11-26
- Question: gart no tiene archivo LICENSE (su ADR 0006 dice «la misma licencia que los demás repos Galivelop», sin fijarla). ¿Lo dejo como pendiente para gart en el aviso?
- Recommendation: Lo decide gart; aquí solo se apunta como pendiente en el aviso (sin licencia no se puede vendorizar ni declarar en THIRD-PARTY.md).

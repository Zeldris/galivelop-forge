# Interfaz TrainerPort y Unsloth como primer extra

<!-- gvc-ddd-decision: q5 -->
Status: accepted

Sección de origen: §4

## Contexto

Hace falta un entrenador, pero el núcleo es solo stdlib y los entrenadores son extras opcionales.

## Decisión

El núcleo define la interfaz `TrainerPort`. El primer extra es Unsloth (LoRA/QLoRA para SFT y DPO), con exportación a GGUF y Modelfile para Ollama (con `ADAPTER` sobre el mismo modelo base exacto, o pesos fusionados). Los demás entrenadores, cuando haga falta.

## Consecuencias

Sin entrenador instalado, `train` falla con la orden que lo instala (invariante 7).

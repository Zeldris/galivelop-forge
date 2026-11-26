# La Steam Deck solo infiere; se entrena en otra máquina

<!-- gvc-ddd-decision: q3 -->
Status: accepted

Sección de origen: §3, §5.6

## Contexto

El modelo ajustado tiene que correr en la Steam Deck, pero esta no sirve para entrenar.

## Decisión

La Deck solo infiere (prompt, Modelfile, medida). LoRA, SFT y DPO se entrenan en una GPU propia o alquilada (Colab), con la máquina y el motivo en la receta. El resultado tiene que correr en la Deck.

## Consecuencias

La receta declara la máquina (`local:<perfil>` o `rented` con motivo). Entrenar en la Steam Deck queda fuera de alcance.

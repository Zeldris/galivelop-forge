# Notas de la release 0.1.0 (parcial, pre-release)

Listas para que un agente local las publique. Nada de esto se ha publicado: el tag y la release los crea quien las
ejecute, con confirmación de la persona.

- **Commit a etiquetar:** `74c2004` (marca de revisión; en `main`, CI en verde). Comprueba que sigue siendo
  ancestro de `origin/main` antes de etiquetar.
- **Tag:** `v0.1.0-pre.1`, como **pre-release**. Se evita `v0.1.0`: el objetivo de la 0.1.0 del roadmap («un export real
  de Tarkor entra como `gforge.dataset/0` válido en gart») **no se ha cumplido** (ver «Falta»). `pyproject.toml` sigue
  en `0.1.0.dev0`; no se toca para esta release.
- **Título:** `gforge 0.1.0 (parcial): capa de datos, sin validar con gart`

## Orden de ejecución (desde el repo, con `gh` autenticado)

```bash
git fetch origin main
git merge-base --is-ancestor 74c2004 origin/main && echo ok   # tiene que decir ok
git tag -a v0.1.0-pre.1 74c2004 -m "gforge 0.1.0 (parcial)"
git push origin v0.1.0-pre.1
gh release create v0.1.0-pre.1 --prerelease \
  --title "gforge 0.1.0 (parcial): capa de datos, sin validar con gart" \
  --notes-file <(sed -n '/^<!-- notas -->$/,$p' docs/records/release-0.1.0.md | tail -n +2)
```

Si `<(…)` no va en el shell, copia el cuerpo de abajo a un archivo temporal fuera del repo y pásalo con `--notes-file`.

<!-- notas -->
## Qué entra

Núcleo `gforge` solo con la stdlib de Python 3.8+. Los entrenadores siguen fuera (llegan en fases posteriores).

- **Paquete y puertos** (0.1.0-1): los puertos vacíos fallan cerrados (invariante 10); el paquete importa sin dependencias (invariante 7).
- **Fuente Tarkor** (0.1.0-4): `gforge.sources.tarkor` lee los exports de destilación y DPO sin ejecutar los scripts del juego. Formato en `docs/sources/tarkor.md`.
- **Filtros** (0.1.0-5): `gforge.filters` rechaza entero, sin editarlo, el ejemplo que contenga un correo, un teléfono o un nombre de una lista que da quien llama, fuera del repo (invariante 2). `gforge.teachers` filtra por una lista de maestros abiertos (invariante 9).
- **Particiones** (0.1.0-6): `gforge.splits` reparte por hash de semilla e id, determinista e independiente del orden; `test` es el lote de reserva del GVE (invariante 3).
- **Datasets** (0.1.0-7, 0.1.0-8): `gforge.datasets.build` criba, parte y escribe `datasets/<objetivo>/<versión>/` con `<partición>.jsonl`, `LICENSE` y `manifest.json`; la licencia viaja y se toma la más restrictiva (invariante 1); una versión publicada no se sobrescribe. `combine` rechaza mezclar CC BY-SA con NC.
- 76 tests; CI en verde sobre la marca de revisión.

## Falta (por eso es pre-release)

- **0.1.0-2 y 0.1.0-3, bloqueadas por gart:** gart aún no tiene código, así que no hay gart vendorizado, ni test de huella sha256, ni validación real de `gforge.dataset/0`. El `manifest.json` es **provisional**. Aviso para gart en `docs/records/aviso-gart.md`.
- **Sin probar con un export real de Tarkor:** lo genera la persona.
- **Lista de maestros abiertos conservadora** (Q-6): abiertos Llama 3.1+/Llama 4, DeepSeek-R1/V3 y gpt-oss; cerrados Claude, GPT, o1-o9 y Gemini; el resto se rechaza hasta que alguien lo añada con su licencia. Los ejemplos de Tarkor con `provider gemini:…` quedan fuera.
- **El filtro de maestros es más laxo de lo previsto en esta versión:** acepta cualquier modelo cuyo nombre contenga un patrón abierto, incluidos llama-3.2 visión y deepseek-r1-distill-llama, que tienen licencia propia. La corrección llegará en la siguiente versión.
- **Python 3.8 en el CI:** `ubuntu-latest` (26.04) ya no la trae; hoy solo `tests/test_py38_syntax.py` lo aproxima.
- Leves conocidos de la revisión, en `docs/records/pending.md`.

## Licencias

Código bajo `LICENSE`; datasets bajo CC BY-NC-SA 4.0 (`LICENSE-content.md`, ADR 0002), sin ejemplos de maestros cerrados (ADR 0007). A Hugging Face no se publica nada con esta release.

# Benchmark — Laya CPU vs GPU sul tempo per chiamata

## Riepilogo

Confronto tra tre run con middleware System1/System2 nuovo:

| Run          | Dispositivo Laya | Pausa | Modelli                                | Test/modello | OK    |
| ------------ | ---------------- | ----- | -------------------------------------- | ------------ | ----- |
| `20261019_3` | **CPU**          | 180 s | 4 (phi3, llama3.2:3b/1b, qwen2.5:1.5b) | 5            | 18/20 |
| `20261020_1` | **GPU**          | 300 s | 4 stessi                               | 5            | 19/20 |
| `20261020_2` | **GPU**          | 300 s | 2 (phi3, llama3.2:3b)                  | 5            | 9/10  |

## Risultati per coppia (modello, test)

### CPU (20261019_3) → GPU (20261020_1)

| Modello      | Test                | CPU (s) | GPU (s) | Delta  | Ratio           |
| ------------ | ------------------- | ------- | ------- | ------ | --------------- |
| llama3.2:1b  | estrazione_json     | 729.8   | 222.3   | -507.5 | 0.30x           |
| llama3.2:1b  | matematica          | 28.3    | 15.5    | -12.7  | 0.55x           |
| llama3.2:1b  | programmazione      | 21.0    | 9.8     | -11.1  | 0.47x           |
| llama3.2:1b  | ragionamento_logico | 33.9    | 12.9    | -21.0  | 0.38x           |
| llama3.2:1b  | sintesi_traduzione  | 254.1   | 167.4   | -86.7  | 0.66x           |
| llama3.2:3b  | estrazione_json     | 815.4   | 509.0   | -306.5 | 0.62x           |
| llama3.2:3b  | matematica          | 54.9    | 37.5    | -17.4  | 0.68x           |
| llama3.2:3b  | programmazione      | 126.5   | 171.6   | +45.1  | 1.36x           |
| llama3.2:3b  | ragionamento_logico | 66.1    | 57.3    | -8.8   | 0.87x           |
| llama3.2:3b  | sintesi_traduzione  | 626.8   | 369.7   | -257.1 | 0.59x           |
| phi3:mini    | estrazione_json     | 1067.6  | 586.2   | -481.4 | 0.55x           |
| phi3:mini    | matematica          | 111.6   | 90.3    | -21.3  | 0.81x           |
| phi3:mini    | programmazione      | 169.2   | 141.0   | -28.2  | 0.83x           |
| phi3:mini    | ragionamento_logico | 69.8    | 43.9    | -25.9  | 0.63x           |
| phi3:mini    | sintesi_traduzione  | 902.9   | 1102.2  | +199.3 | 1.22x ⚠ timeout |
| qwen2.5:1.5b | matematica          | 28.1    | 24.8    | -3.2   | 0.88x           |
| qwen2.5:1.5b | programmazione      | 91.1    | 30.2    | -61.0  | 0.33x           |
| qwen2.5:1.5b | ragionamento_logico | 18.4    | 14.3    | -4.1   | 0.77x           |

### Repliche GPU (20261020_2) vs GPU prima (20261020_1)

| Modello     | Test                | GPU1 (s) | GPU2 (s) | Delta  | Ratio |
| ----------- | ------------------- | -------- | -------- | ------ | ----- |
| llama3.2:3b | estrazione_json     | 509.0    | 547.4    | +38.5  | 1.08x |
| llama3.2:3b | matematica          | 37.5     | 39.6     | +2.1   | 1.06x |
| llama3.2:3b | programmazione      | 171.6    | 151.9    | -19.8  | 0.88x |
| llama3.2:3b | ragionamento_logico | 57.3     | 42.8     | -14.5  | 0.75x |
| llama3.2:3b | sintesi_traduzione  | 369.7    | 444.9    | +75.2  | 1.20x |
| phi3:mini   | matematica          | 90.3     | 76.8     | -13.4  | 0.85x |
| phi3:mini   | programmazione      | 141.0    | 197.0    | +55.9  | 1.40x |
| phi3:mini   | ragionamento_logico | 43.9     | 58.7     | +14.8  | 1.34x |
| phi3:mini   | sintesi_traduzione  | 1102.2   | 616.0    | -486.2 | 0.56x |

## Mediane per modello

| Modello      | CPU n | CPU mediana | GPU1 n | GPU1 mediana | GPU2 n | GPU2 mediana |
| ------------ | ----- | ----------- | ------ | ------------ | ------ | ------------ |
| llama3.2:1b  | 5     | 33.9 s      | 10     | 15.5 s       | —      | —            |
| llama3.2:3b  | 5     | 126.5 s     | 10     | 171.6 s      | 10     | 151.9 s      |
| phi3:mini    | 5     | 169.2 s     | 10     | 141.0 s      | 8      | 136.9 s      |
| qwen2.5:1.5b | 3     | 28.1 s      | 8      | 27.5 s       | —      | —            |

## Conclusioni

### 1. Effetto medio CPU→GPU: -33.6% (delta medio), -37.1% (mediano)

Su 18 coppie confrontabili, la maggior parte mostra una riduzione di tempo passando da CPU a GPU. Il delta medio è **-33.6%** e il mediano **-37.1%**. Questo indica che **Laya su GPU accelera l'inferenza Ollama**, non solo le chiamate Laya.

### 2. Ma il tempo dominante è Ollama, non Laya

I tempi registrati includono l'intera pipeline (middleware + inferenza Ollama). Le chiamate più lunghe (>600 s) sono quasi tutte su test con input lungo (`estrazione_json`, `sintesi_traduzione`) dove il collo di bottiglia è l'inferenza del modello, non il routing Laya. Spostare Laya su GPU riduce i tempi ma non elimina i timeout.

### 3. Variabilità alta nelle repliche GPU

Le due repliche GPU (20261020_1 vs 20261020_2) mostrano variazioni fino a ±40% per stessa coppia (modello, test). La mediana di phi3:mini passa da 141 s a 136.9 s, quella di llama3.2:3b da 171.6 s a 151.9 s. **La variabilità intra-GPU è comparabile all'effetto CPU→GPU**, quindi l'effetto non è statisticamente robusto con poche repliche.

### 4. Decisione

**Spostare Laya su GPU produce un beneficio misurabile ma non risolutivo.** I tempi medi scendono di circa un terzo, ma:

- La variabilità tra repliche è significativa (±20-40%)
- I timeout su test lunghi persistono (collo di bottiglia è Ollama, non Laya)
- Il tetto dei token non è influenzato (causa nel percorso di prompt, già documentato)

**Non chiudere la voce su `ToDo.md`**: servono più repliche per stabilire significatività statistica.

## Archivio

Script di estrazione: `benchmark/scripts/benchmark_cpu_gpu.py`
Dati grezzi: `benchmark/history/20261019_3/`, `benchmark/history/20261020_1/`, `benchmark/history/20261020_2/`

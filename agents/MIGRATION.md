# Migrazione AgentFactory → HAL

- Sorgente acquisita: commit `d1b7e7909b9962ed4cb14ef5107c2fe1845e04c1`.
- Destinazione canonica: `HAL/agents/`.
- Stato: AgentFactory è deprecato; da questo cutover gli aggiornamenti vanno fatti solo in HAL.
- Contenuto mantenuto: L0, 14 L1, competenze, template, riferimenti, script, documentazione, snapshot vendor tracciati e skill L2 `harness-agentfactory`.
- Esclusioni: `.git`, `.env`, `dist/` generato, `.venv`, `__pycache__` e configurazione `.cursor/` specifica del repository AgentFactory. La skill L2 è stata importata separatamente in `project-skills/`.
- Compatibilità: `.agents/skills/` è l'entrypoint condiviso Zed/Cursor; `.cursor/agents/` e `.cursor/commands/` sono adapter Cursor.
- Modello: l'esecuzione usa System 2 predefinito, `SystemTwoEngine.ACTIVE_MODEL_NAME`.

La migrazione iniziale conserva i contenuti senza razionalizzarli. Il repository sorgente non è stato modificato né cancellato.

## Struttura canonica successiva

La struttura HAL attuale consolida i 14 bundle L1 originari in 7 L1, mantenendo le specializzazioni come skill integrate:

| Bundle originario | Destinazione strutturale in HAL |
|---|---|
| `a-b2b`, `a-copywriter`, `a-harness`, `a-product`, `a-seozoom`, `a-wordpress` | L1 omonimo |
| `a-enrichment` | Skill `enrichment` nel dominio `a-b2b` |
| `a-charts`, `a-illustrator`, `a-uiux` | Skill `charts`, `illustrator`, `uiux` nel dominio `a-design` |
| `a-po` | Consolidato nel dominio `a-product` |
| `a-gherkin`, `a-jtbd`, `a-personas` | Skill omonime nel dominio `a-product` |

Questa mappa descrive la collocazione dei contenuti nell'albero HAL, non certifica la parità funzionale di ogni istruzione, riferimento o script con il repository AgentFactory. AgentFactory resta deprecato e non è una fonte operativa.

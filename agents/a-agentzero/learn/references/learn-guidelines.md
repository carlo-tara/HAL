# /learn — Guide Operative

## Cosa conta come «appreso»
- Preferenze esplicite dell'utente (formato, tono, vincoli, «sempre», «mai»)
- Correzioni ripetute o correzioni puntuali con intento permanente
- Convenzioni progetto scoperte o confermate (path, workflow, naming)
- Pattern validati in questa sessione (es. notazione `60'`, JSON-first PED)
- Invarianti o failure condition emersi da debug
- Follow-up / debito / «da fare dopo» confermati (→ candidati `./ToDo.md`)
- Lacune di glossario / BC / howto locali (→ candidati docs)

**Escludi:**
- Task completati in sessione («fixa questo bug» fatto e chiuso)
- Dati sensibili, credenziali, token, path a `.env`
- Metriche non verificate
- Ipotesi non confermate
- Contenuto già presente identico nelle skill/docs

## Destinazione (routing)
| Destinazione | Quando (necessario) |
|--------------|---------------------|
| **Skill / brand / rules** | Preferenza o convenzione **permanente** che l'agente deve riapplicare. |
| **`./ToDo.md` (Attività)** | Residuo **actionable** non ancora slice (follow-up, bug, wave successiva). |
| **Doc locale** | Spiegazione / confini / howto che non è regola agente (es. glossario). |
| **Escludi** | Ephemeral, fatto, sensibile, non confermato. |

## Ambito: Progetto vs HAL
- **Progetto:** Convenzione/preferenza del repo consumer (o delta L2 locale). (Es. `.cursor/skills/...`, brands, rules, `./ToDo.md` consumer).
- **HAL:** Protocollo / L0 / L1 canonici / harness meta-repo (Es. `a-*/`, `harness-agentfactory`, docs AF, `./ToDo.md` AF).

## Regole di scrittura
1. **Delta only** — nel L2 non copiare intere sezioni già in L0/L1; aggiungi o precisa.
2. **Una idea, un posto canonico** — integra voci esistenti invece di crearne parallele.
3. **Stesso lessico del file target**.
4. **Mai** scrivere segreti.
5. **L1 globale** — modifica solo se su richiesta esplicita o se il pattern è validato su >=2 progetti.
6. **Anti-grasso** — se l'apprendimento è già coperto da padri, segnala e non gonfiare il L2.

## Esempi
- **Esempio `?`**: Report con voce "notazione 60'" destinazione skill, voce "allineare pin" destinazione ToDo.
- **Esempio `!`**: Integra regola in `writing-rules.md`, appende ToDo, scrive Changelog, fa bump patch su skill toccate.

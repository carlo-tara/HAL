# Analisi generalizzazione L2 → L1 / L0 (`/sync <`)

Criteri operativi per la modalità **`/sync <`**: scansionare skill L2 nei progetti consumer e proporre cosa promuovere verso L1 o L0. **Zero scrittura** — solo report.

Allinea a [consolidation-targets.md](../../learn/references/consolidation-targets.md) e [AGENT-PROTOCOL.md](../../AGENT-PROTOCOL.md).

---

## Principio

| Resta L2 | Sale a L1 | Sale a L0 |
|----------|-----------|-----------|
| Path, `.env`, brand, lessico, cluster keyword, template editoriali di prodotto, soglie sito | Pattern di dominio riusabili tra siti (≥2 progetti o richiesta esplicita) | Protocollo, sync, scaffold, invarianti cross-agente |

**Anti-grasso:** se L2 ridice il padre → raccomandare **taglio + puntatore**, non promozione.

---

## Input

| Sorgente | Uso |
|----------|-----|
| Path progetto(i) dopo `/sync <` | Scan `{repo}/.cursor/skills/*/SKILL.md` |
| Repo corrente se nessun path | Default: workspace attivo |
| Catena `extends:` | Confrontare ogni L2 col padre L1 (e L0) |
| `role:` multi-figlio | Separare data / editorial / voice / default |

---

## Classificazione per voce trovata

Per ogni sezione/regola/workflow nel body L2 (e reference locali non dati):

| Classe | Criterio | Azione proposta |
|--------|----------|-----------------|
| **DUP** | Già coperto da L1/L0 (stesso significato) | Tagliare L2; lasciare rimando |
| **L1** | Dominio riusabile; path/script restano L2 | Promuovere canone/competenza L1; L2 = delta |
| **L0** | Protocollo, discovery, sync, scaffold, sicurezza soft | Promuovere in a-agentzero / competenze L0 |
| **L2** | Identità progetto, path assoluti, metriche sito, brand | Nessuna promozione |
| **NEED-N** | Sembra L1 ma visto in un solo progetto | Segnalare; promuovere solo se utente conferma o compare 2° sito |

---

## Heuristic di scansione

1. Elenca skill con `extends: a-*` (e fallback legacy) sotto `.cursor/skills/`
2. Per ciascuna: leggi frontmatter (`role`, `extends-version`) + sezioni Workflow / Override / Regole / Checklist / Deleghe
3. Confronta col padre L1 (SKILL + competenze dichiarate) e, se rilevante, L0
4. Cerca pattern ripetuti **tra progetti** se `/sync <` ha ≥2 path
5. Segnala L2 grassi (sezioni lunghe che solo puntano a L1) come debito **DUP** prioritario
6. Non inventare metriche SEO; non proporre di spostare `.env` o path hardcoded

### Segnali tipici → L1

- Limiti piattaforma (es. Substack title/preview) senza brand
- Procedure QA tecniche (es. no-fill firme)
- Algoritmi batch/manifest generici
- Publication-types / JSON-first senza path progetto
- Keyword CSV ≠ copy letterale

### Segnali tipici → L0

- Discovery multi-figlio, companion sync, template deleghe
- Regole `/learn` / `/sync`, versionamento
- Brand vs voice skill (principi, non corpus)

### Segnali tipici → resta L2

- Working directory, `SEOZOOM_PROJECT`, GSC property
- Lessico vietato di brand, voice corpus, template 5 sezioni prodotto
- Cataloghi URL live, lead magnet specifici

---

## Priorità nel report

1. **DUP** (debito grasso) — alto impatto, rischio basso
2. **L0** — se protocollo rotto o assente
3. **L1** con evidenza ≥2 progetti
4. **NEED-N** — candidati singoli progetto
5. **L2** espliciti — solo se l'utente chiede inventario completo

---

## Cosa non fa `/sync <`

- Non modifica file (né L2 né L1/L0)
- Non esegue `deploy-all` né bump `extends-version`
- Non sostituisce `/sync ?` (versioni) né `/learn ?` (sessione chat)
- Per applicare: dopo conferma utente, edit mirati + CHANGELOG; oppure `/learn !` con target L1 se l'apprendimento nasce da chat

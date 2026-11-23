# Pre-commit (L0)

## Objective

Verificare che le modifiche siano pronte per il commit nel **repository corrente** e proporre messaggio e comando `git`. Non eseguire il commit a meno che l'utente non lo chieda esplicitamente.

## Process

1. **Diff-tiering (System 1 & pre-filtraggio):**
   - Esegui `git status -s` e `git diff --stat`.
   - Se il diff totale > 150 righe, ispeziona solo i chunk o file modificati rilevanti (escludendo vendor, lockfile, asset autogenerati).
   - Usa `python3 router.py choice "Scegli il prefisso conventional commit per queste modifiche" --options "feat: aggiunge comportamento visibile all'utente, fix: ripara comportamento già previsto, docs: solo documentazione, chore: manutenzione (deps/config) senza cambio di comportamento, refactor: cambia struttura preservando il comportamento" --json` per determinare il tipo a costo zero token e catturare l'eco `request_hash` della scelta (serve al passo 7; senza `--json` resta la sola label). Le opzioni semanticamente adiacenti vanno passate **sempre** in forma `label: gloss` con la regola di confine (S1, telemetria 2026-11-16: confusion matrix `refactor→feat` 16 voti, `docs→skill` 20): il layer MCP inietta inoltre le boundary rule note per le coppie confusibili. Per il voto del passo 7 il flusso è invariato.
2. Dalla **root del repository** attivo:
   - Identificare area toccata (src, docs, test, config, skill, …) in base all'output precedente.
3. **Segreti**: niente `.env`, credenziali, token, chiavi API nei file tracciati.
4. **Verifiche contestuali** (solo se esistono e sono pertinenti al diff):
   - script/test documentati in `README.md`, `package.json`, `Makefile`, `CONTRIBUTING.md`
   - lint/test del linguaggio in uso
   - doc operativa se cambiano contratti pubblici
5. Se il repo ha skill agenti HAL: allineamento `version` / `extends-version` / `CHANGELOG` se il diff tocca skill (vedi anche `/version`, `/sync`).
6. Generare messaggio di commit (conventional) ed eseguire il commit **a index isolato** (§Isolamento index): `bash /var/www/hal_gateway/agents/a-agentzero/scripts/agent-commit.sh -m <msg-file> [-a <extra-hook>] [--push] -- <path>...` — path assoluto del canonico: invocazione identica da hal_gateway e da qualunque consumer (i mount `.agents`/`agents` non esistono più). Su repo mono-sessione il classico `git add … && git commit -F <msg-file>` resta ammesso, ma la whitelist dei path va comunque dichiarata esplicita (mai `git add -A`, mai `git commit -a`).

7. **Auto-voto post-commit (T-33B98, approvato con ok steward esplicito 2026-11-09):** dopo che `git commit` è riuscito con esito 0, registra la verità esterna sul loop di calibrazione Laya:
   - `python3 /var/www/hal_system1/scripts/auto_vote_commit.py --hash <request_hash del passo 1> --expected <prefisso realmente scritto>` — voto cieco con `source='commit'`: il server calcola `correct|incorrect` dal confronto con la scelta archiviata e il voto sostituisce, una sola volta, un eventuale voto implicito S2 di autorità minore (mai un altro commit).
   - Il voto va scritto **anche a dissent zero** (correct implicito): è il flusso di calibrazione, non una lamentela.
   - Se il passo 1 non ha prodotto `request_hash` (servizio giù, ABSTAIN, scelta manuale senza eco), **salta** il voto: mai inventare o riutilizzare hash di altre righe. L'helper esce 0 anche su `no-vote`; non far mai fallire il commit per colpa del voto.
   - Per le scelte `laya_routing` la verità esterna è il file/bersaglio realmente modificato: dopo commit riuscito, `python3 /var/www/hal_system1/scripts/auto_vote_routing.py --hash <request_hash ecoato da laya_routing> --options "<insieme opzioni della chiamata>"` — il helper deriva l'etichetta dal diff dell'HEAD (`.agents/skills/**`→skill, `ToDo.md`→ToDo, `docs/**`/`*.md`→docs), vota cieco con `source='routing'` (autorità esterna come commit, provenienza distinta nel report) e non vota se il bersaglio non è classificabile o l'etichetta è fuori dall'insieme opzioni. Come il voto commit: esce 0 anche su `no-vote`, mai far fallire il commit per colpa del voto (override esplicito: `--expected <label>`).

## Isolamento index (gare multi-sessione)

`git commit` legge **l'index condiviso** del repository, non «ciò che ho aggiunto io». Con più sessioni agente sullo stesso worktree si osservano le due facce della gara: il reset altrui azzera l'add mio (commit vuoto/parziale, AGG-10) e il mio commit assorbe i file altrui già stageati (recidiva brainbeez release 0.14.0, 2026-11-16: 9 file WIP parallelo finiti nel mirror commit). Protocollo:

1. **Allow-list P**: decidere PRIMA i path esatti del proprio slice (delta-only); mai `git add -A` selvaggio su repo condiviso.
2. **Commit con `scripts/agent-commit.sh`**: index privato (`GIT_INDEX_FILE` seminato da `git read-tree HEAD`), `flock` cooperativo, guardia pre-commit (`staged ⊆ P`: path esatti o prefissi di directory), audit post-commit (`committed ⊆ P ∪ extra`), push con verifica `git ls-remote` (il «Everything up-to-date» bug: fidarsi solo del confronto remote-sha == local-sha, retry 1x). Gli hook git ereditano l'ambiente: un pre-commit che rigenera file (`git add` in hook) scrive nell'index privato — dichiararlo con `-a <path>`. In chiusura lo script riallinea l'index condiviso (`env -u GIT_INDEX_FILE git add -A -- <P>`, ammette directory; `update-index` le rifiuta) sui soli path committati: un commit out-of-band lascia l'index al vecchio HEAD e un `git commit` ingenuo altrui commetterebbe un revert-fantasma (scoperta al dogfood, 2026-11-16). Mai `git reset` su repo condiviso: cancellerebbe lo staged altrui.
3. **Fallback senza script**: `git commit -F <msg> -- <path>...` (pathspec-limited: impegna il work-tree dei propri path e ignora l'index altrui) + audit manuale `git diff-tree --no-commit-id --name-only -r HEAD ⊆ P`. Limite del fallback: legge il work-tree, quindi edit paralleli _sugli stessi file_ restano un rischio.
4. **Recupero dichiarato** se l'audit becca file inattesi: `git reset --soft HEAD^` (muove solo il ref; l'index condiviso altrui resta intatto) e ritentare con allow-list corretta. Prima di ritentare verificare lo stato reale con `git status <file>`: il ripristino della prosa altrui nel worktree può essere annullato dal loro tooling (loro si ri-registrano) — mai riaprire la corsa sullo stesso file. Mai `reset --hard` su repo condiviso.
5. **Limiti residuali**: l'isolamento protegge l'index, non il work-tree. Stesso file in due mani ⇒ discipline a monte (write set disgiunti tra deleghe, o `git worktree` per sessione). Il `flock` serializza solo chi passa di qui: regola di adozione, non garanzia assoluta. **Mitigazione operativa** (evidenza `hal_mcp_docs` `5d04050`, 2026-11-22: audit post-commit corretto — `1 file ∈ allow-list` — ma 3 righe di una sessione parallela nel diff, perché quel file è cambiato tra il censimento e il commit): ricontrollare `git status --porcelain -- <file>` **immediatamente prima** di invocare lo script, non all'inizio della ricognizione; con più sessioni attive sullo stesso file passare a `agent-worktree.sh` invece di condividere il checkout; dopo il commit auditare le righe realmente entrate (`git show HEAD --format= --unified=0 -- <file>`) e, se l'assorbimento è avvenuto, dichiararlo — mai `reset`/revert su un ref già pushato.

6. **Taglio release con registro misto (blob surgery)** — quando `[Unreleased]` del CHANGELOG contiene voci chiuse da altre sessioni NON nel tuo scope, mai stageare il worktree (committeresti la prosa altrui): costruire il blob da `git show HEAD:<file>` e iniettare solo la propria sezione (`git hash-object -w --stdin` + `update-index --cacheinfo`); `git apply --cached` fallisce sulle righe-tabella lunghe (context mismatch). La base del blob è la **HEAD del momento**, non quella di inizio sessione: con tagli paralleli che avanzano HEAD, ri-verificare `git diff --cached` contro la HEAD viva subito prima di committare e ricostruire il blob se è mossa; mai inferire il contenuto dell'index dallo `--stat` dei commit altrui — solo `git diff --cached` fa fede. (Evidenza: recidiva brainbeez release 0.14.0; tagli 0.15.0/0.16.0/0.16.1 applicano la ricetta.)
## Checklist

- [ ] Diff compreso; scope del commit chiaro
- [ ] Nessun segreto nel commit
- [ ] Test/verifiche rilevanti eseguiti o motivati se saltati
- [ ] Doc aggiornata se cambiano contratti o workflow
- [ ] Messaggio conventional coerente col diff
- [ ] Allow-list P dichiarata; commit via `agent-commit.sh` (o pathspec-limited + audit) su repo condiviso
- [ ] Audit post-commit passato (`committed ⊆ P ∪ extra-hook`); push verificato con `ls-remote` se `--push`

## Commit message (conventional)

Esempi:

- `feat:` nuova funzionalità
- `fix:` correzione bug
- `docs:` solo documentazione
- `chore:` tooling, dipendenze, config
- `refactor:` ristrutturazione senza cambio comportamento

Messaggio in **frasi complete**, lingua coerente col resto del repo.

## Expected output

- **Nessun preambolo o saluto.**
- **Nessuna ripetizione** della checklist statica.
- Esito test verificati (una riga).
- Blocco di codice con il comando `agent-commit.sh …` (o la coppia `git add -- <P>` + `git commit -F <msg>`) pronto al copia-incolla.

## Usage

```
/commit
```

## Notes

- Baseline L0: `a-agentzero/commands/commit.md`.
- Fonte: canonico hal_gateway, pubblicato come skill globale `~/.agents/skills/commit` (priorità: skill di progetto > globale). Override progetto: file reale `{repo}/.agents/skills/commit/SKILL.md`.
- Per snapshot stato repo usare `/snapshot` se disponibile nel progetto.

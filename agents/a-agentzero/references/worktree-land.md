# Protocollo di concorrenza e merge per sessioni parallele

**Regola d'oro:** il worktree isola la *concorrenza*, il branch sposta il
*conflitto* dal silenzio (ultimo-scrittore-vince) al merge (3-way, esplicito,
revisionabile). Servono entrambi: `agent-worktree.sh`.

## Ciclo di vita di una sessione

```bash
bash agents/scripts/agent-worktree.sh new <nome>     # branch slice/<nome> da origin/master
cd /var/www/.wt/hal_gateway-<nome>                   # apri QUI la sessione Zed
# ...lavoro, commit...
bash agents/scripts/agent-worktree.sh land <nome>    # preview → rebase → guardie → push ff → cleanup
```

- `new` crea anche `<wt>/.tmp/`: lo stato temporaneo vive lì, **mai** `/tmp`
  condiviso (gara di nomi prevedibili: 2026-11-18, `/tmp/learn_state.txt`).
- Ogni `land` prende il **flock cooperativo `agent-commit.lock`** (già usato da
  `agent-commit.sh`): il land è l'unico punto di serializzazione su master.
- Il gate del land: `make -C agents pre-commit` (include `check-registry`) —
  se il pre-commit del branch è verde, main resta verde per costruzione.

## Le 13 regole

Disciplina (zero codice):
1. La metrica del WIP non è più il tree sporco ma **l'età del branch al land**:
   `agent-worktree.sh status` avvisa oltre 4h. Ogni ora aperta è interesse sul conflitto.
2. I write-set disgiunti diventano **dichiarati**: il write-set è
   `git diff --name-only origin/master...<branch>`; git inoltre **vieta** lo
   stesso branch in due worktree.
3. Temporanei nel worktree (`.tmp/` già session-scoped dal path); `/tmp` è
   globale sull'host anche coi worktree — usarlo solo con suffisso session-id.
4. La verifica pre-land è **una sola**, deterministica: `git merge-tree
   --write-tree origin/master HEAD` (preview dei conflitti) invece di sei
   sonde post-render troncate.
5. La tripletta: **worktree (concorrenza) + branch (merge) + land seriale
   (serializzazione)**. L'una senza l'altra è isolamento di carta.

Strumentali (codice):
6. Transazione bump↔changelog chiusa da `agents/scripts/check-version-changelog.sh`
   (`--fix` inserisce lo stub): ogni `version:` in frontmatter ha il proprio
   `## [v]` nel changelog sorella. Abolisce l'archeologia tipo [1.6.16]/[1.11.0].
7. Cap di 3000 byte per riga sui registry (`check-line-length.sh`, wired in
   `check-registry` → bundle `pre-commit`): il 3-way di git è **a righe**, una
   riga da 7k char è un conflitto intero manuale. Le righe-evidenza vanno tenute
   un-item-per-bullet (split verificato: `split_monsters.py`).
8. Il lock single-writer per `/learn !` non serve più come pretesa: i registri
   **si mergeano** (union/rerere), il claim sopravvive solo sul land (flock).
9. Il land è sequenza unica: preview → rebase → guardie → `make -C agents
   pre-commit` → push ff-only + verifica `ls-remote` → allineamento main +
   link-mirror → cleanup worktree/branch.
10. Un branch, un slice, un turno: mai due slice aperte nella stessa sessione;
    land entro il turno.
11. I registry sono **progettati per il merge**: `merge=union` sui puri
    append-only (`.gitattributes`), `rerere.enabled` per i pattern ripetuti
    (header di versione, `extends-version`); ToDo.md **non** è union (è
    rinfrescabile, l'union duplicherebbe i rewrite).
12. La allow-list dei commit di `agent-commit.sh` (staged ⊆ P) viene sostituita
    dal **diff del branch** dichiarato al land: controllabile da macchina e
    rivedibile da umano *prima*, non dopo.
13. I consumer (`hal_system1/agents → .../agents`, mirror `.agents/skills`)
    vedono il main checkout: il WIP è **strutturalmente invisibile** finché
    non landa. Dopo il land: `link-workspace-skills.sh` (automatico nel land se
    main è pulito) + `/sync !` per `~/.cursor`.

## Costi onesti del modello

- La **coda del land** è il nuovo collo di bottiglia: va mantenuto un gesto di
  secondi (rerere + union + cap lo rendono tale).
- I conflitti restano possibili (git è a granularità di riga): sono solo
  espliciti e risolvibili, non silenziosi.
- La disciplina "un branch, un turno" non è meccanica: è l'unica regola d'onore
  che sopravvive (vedi `status`).

## Telemetria del protocollo

I gate del bundle (`make -C agents pre-commit`) sono la prova di mergeabilità:
un land che passa è un main che resta verde.

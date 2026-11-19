# 29 — Apprendimenti di sessione: de-racing multi-progetto (2026-11-19/20)

Nota datata prodotta da `/learn !`. I target canonici di queste voci
(`agents/a-agentzero/learn/references/tool-pitfalls.md`,
`agents/a-agentzero/learn/CHANGELOG.md`, `product/session-learnings.md`) erano
WIP di sessione parallela al momento del consolidamento: il testo canonico
vive qui, pronto per il riversamento (Attività in `./ToDo.md` con puntatore).

## Ambito: HAL

### 1. Strumenti: risultati replay/stale del canale tool

**Classe nuova** (distinta da §Output lunghi/frammenti): il canale dei
risultati tool può restituire l'output di una chiamata PRECEDENTE invece
dell'attuale, senza errore evidente. Evidenza 2026-11-19/20 (hal_gateway):

- `cat ToDo.md` e `read_file ToDo.md` che rispondono la stessa riga isolata
  (contenuto di una lettura precedente) a fronte di file da 37 righe integro
  (verificato con `wc -l` + `md5sum` + `sed -n 'X,Yp'`);
- coppia parallela «`echo "===HEAD==="; git log` + lettura gate» che mostra
  HEAD vecchio mentre lo stato reale era già quello nuovo;
- script `/tmp/*.sh` scritti in una chiamata e `bash /tmp/x.sh` in chiamata
  parallela alla stessa risposta → `exit 127: file o directory non esistente`
  (la scrittura non era ancora avvenuta al momento dell'esecuzione).

**Canone operativo**:

1. mai parallelizzare producer→consumer dello stesso path (script /tmp,
   file appena scritto): sequenziare in chiamate distinte;
2. ogni claim di stato (commit, push, rigenerazione, file integro) va
   riaffermato con un secondo comando di forma DIVERSA (`ls-remote`,
   `md5sum -c`, `wc -l` + marker unico `echo "TAG-$(date +%s)"`);
3. un output che «sembra vecchio» non è prova: riverificare prima di
   correggere o riapplicare (è la regola-8 estesa al canale risultati).

### 2. Mirror generati: through-write dei symlink verso il canone

**Classe nuova** (estensione di §Path dei comandi L0: canonico vs mirror):
quando un percorso di mirror è stato storicamente un symlink verso il file
canonico, ogni writer che fa `mkdir -p` + scrittura sul path scrive
ATTRAVERSO il link e corrompe il canone. Evidenza (allerta 2026-11-19,
promozione sync/learn a comandi L0): `.agents/skills/{sync,learn}` symlink
verso `agents/a-agentzero/{sync,learn}`; `link_zed_skill` (mkdir + `open(w)`
su `skill_dir/SKILL.md`) avrebbe sovrascritto il SKILL.md del bundle con il
wrapper; `publish-global-commands.sh` (cmp + `mv`) equivalente attraverso il
symlink globale `~/.agents/skills/{sync,learn}` creato lo stesso giorno.

**Canone operativo**:

1. i writer di mirror rifiutano la destinazione symlink:
   «Guardia anti-through-write» in `link_zed_skill` (commit 67f365f) e
   rm-guard nel loop di `publish-global-commands.sh`;
2. prima di cambiare modello di pubblicazione a un nome esistente: rimuovere
   fisicamente i symlink residui, poi rigenerare, e provare l'illesità dei
   canoni con md5 prima/dopo;
3. la scelta del modello di pubblicazione (symlink-canone-live vs
   wrapper-generato) va dichiarata nel §Notes della skill coinvolta
   (sync 1.2.2 docet).

### 3. Push respinto dal gate pre-push del repo su WIP altrui

**Estensione §Sessioni parallele**: l'hook pre-push valuta il WORKING TREE
condiviso, non solo il commit: (brainbeez, push del fence tpl 2, 2026-11-20)
`make check-static` in docker falliva per 3 errori ruff nel WIP non
committato di un'altra sessione (`unused hashlib` in due test, un `RUF100`).
**Canone operativo**: non sistemare il lint altrui per far passare il proprio
commit; lasciare il commit locale fast-forward-ready, avvisare il
proprietario della slice; mai `--no-verify` per aggirare il gate (il gate è
la verità del repo).

### 4. Brace `{a,b}` sotto sh — secondo incontro, promozione matura

Estensione di §Shell di lavoro sh/dash: non è solo `<( )`: anche
l'espansione di brace NON avviene (dash). Ricorrenze: brainbeez 2026-11-18
(`ls agents/a-{...}`, pathspec di `git commit --`) + hal_gateway
2026-11-19 (`mkdir -p .../commands/harness-{mcp,orchestration,router}` →
creata una directory letterale `{mcp,orchestration,router}`). Il criterio
della voce ToDo («promuovere a tool-pitfalls alla seconda sessione») è
soddisfatto: blocco pronto per il riversamento in §Shell di lavoro sh/dash.

### 5. Chiavi di idempotenza: devono coprire tutto ciò che è generato

**Classe trasversale (infra)**: `fence_state` di hal-contract.py confrontava
solo la versione del canone; una modifica al SOLO template del fence non
avrebbe rigenerato nessun consumer. Fix tpl 2 (commit 719b278): marcatore di
template nel fence e refresh forzato a versione invariata. Regola generale:
quando un artefatto derivato è cachato da una chiave di versione, la chiave
deve coprire template + sorgente (o serve un marcatore template dedicato).

## Changelog HAL (da riversare in `product/session-learnings.md` §HAL)

- 2026-11-19/20 — de-racing completo hal_gateway↔consumer: guardia realpath
  su rigenerazione (1.13.10), L2 nei repo proprietari (1.13.11), contratto
  + catalogo fence `hal-contract.py` (1.13.12), comandi L0 globali
  `~/.agents/skills` + sync/learn promossi a comandi (67f365f), delega MCP
  `skills_list`/`skill_read` per L1/embedded (hal_mcp_tools 1.10.0). Appresi
  i canoni 1–5 di questa nota.

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
devono coprire template + sorgente (o servire un marcatore template dedicato).

### 6. Lista consumer: tre liste hardcode divergenti → fonte unica

**Classe nuova (governance dati)**: l'insieme dei repo consumer era hardcodato
in tre posti in disaccordo — `hal-contract.py` (11 repo),
`prune-local-commands.py` (11), `sync-consumer-stale.sh` (10) → 19 unici,
intersezioni parziali. Il dry-run di `hal-contract.py` ha misurato i mount
reali non coperti da nessuna lista: **pickwaise 41 symlink, liberating.it 18,
gDrive_ops 2** — i consumer con più drift erano invisibili al fence.

**Canone operativo:**

1. Fonte unica `agents/consumers.list` (un path per riga, `#` commento,
   hal_gateway escluso) + loader `agents/scripts/consumers_list.py`
   (`load_consumers()`; CLI `--strict` / `--paths`).
2. `hal-contract.py` e `prune-local-commands.py` importano il loader;
   `sync-consumer-stale.sh` carica `PROJECTS` con `mapfile` dallo stesso
   file. Guardia sul canone («canone, mai toccato») ora presente in entrambi
   gli applicatori — prima solo in prune.
3. Gate: `make -C agents consumers-list` (report; `STRICT=1` → exit 1 su
   path mancante). NON in pre-commit: i repo consumer possono mancare su
   altre macchine.
4. Aggiungere/rimuovere un consumer = UNA riga nella lista, non tre script.

**Evidenza:** sessione de-racing HAL 2026-11-20 — conteggi da tool result
(dry-run hal-contract, verifica ad-hoc delle liste, `make consumers-list`
exit 0 su 21/21).

### 7. Claim nata da decodifica parziale: ed è FINITA in un artefatto spedito

**Estensione della classe «Percorsi citati come evidenza vanno verificati»**
(2ª occorrenza; la 1ª restava in chat/ToDo, qui il fatto falso è stato
persistito): ricucendo output terminaltroncati/base64 ho «letto» un
inesistente `/var/www/semidifosing` in hal-contract.py e l'ho scritto come
prova di drift nel docstring di `consumers_list.py`. Un `grep -rn` autoritativo
su tutto l'albero ha mostrato che la stringa esisteva **solo nel mio file**:
una fabbricazione da decodifica — e spedirla in un sorgente la rende persistente.

**Canone operativo:**

1. Ogni fatto (path, nome, numero) prima di essere scritto in un artefatto
   durevole va riverificato con un comando read-only sull'albero reale — la
   decodifica di un output di trasporto NON è evidenza.
2. Se il tool restituisce output monchi o una singola riga spuria al posto
   del contenuto (visto su `sync-agents.sh` e `agents/Makefile`), la via è
   `base64 -w0` o `json.dumps` del testo — e comunque riverificare con grep
   mirato prima di asserire.
3. Regola 9 di `learn-guidelines.md` (numeri: verbatim o rimisura) estesa ai
   fatti stringuali.

### 8. `grep --include=*.py` non quotato: la shell lo espande

**Variante di §Shell di lavoro sh/dash**: `sh` espande i glob NON quotati sul
CWD prima di passarli a grep. `grep -rn "..." --include=*.py --include=*.sh .`
con un `.py` presente in root ha cercato SOLO quel file, producendo un
negativo plausibile ma FALSO («nessun altro riferimento»). Rischio
particolare: il negativo finisce in una conclusione o in un ToDo.

**Canone operativo:** quotare sempre i pattern (`--include='*.py'`); prima di
asserire un'assenza, positive control con una stringa che DEVE esserci.

### 9. Stato condiviso dentro la stessa batch di tool call

**Variante di §Tool call paralleli + §Sessioni parallele (campo /tmp)**:
(a) `python3 verify-x.py` e `delete_path verify-x.py` emessi nella STESSA
risposta: il re-read successivo restituiva output vuoto perché il delete
era già avvenuto — «exit 0 senza stdout» sembrava «script muto». (b) file
`/tmp/l6.txt` scritto dalla chiamata-1 e rileto dalla chiamata-2 parallela:
«non esiste» — le chiamate parallele non sono ordinate fra loro. (c) gli
script usa-e-getta scritti in root di repo SENZA prefisso `.tmp_` sono
entrati nel `git status` condiviso con la sessione parallela (pericolo di
assorbimento in allow-list — cfr. HT-012).

**Canone operativo:** stesso artefatto → chiamate SEQUENZIALI (run, POI
delete); stato intermedio → `.tmp_*` nel root del progetto, rimosso subito;
`/tmp` grezzo solo per dump one-shot riletti nella stessa chiamata che li
produce.

## Changelog HAL (da riversare in `product/session-learnings.md` §HAL)

- 2026-11-19/20 — de-racing completo hal_gateway↔consumer: guardia realpath
  su rigenerazione (1.13.10), L2 nei repo proprietari (1.13.11), contratto
  - catalogo fence `hal-contract.py` (1.13.12), comandi L0 globali
    `~/.agents/skills` + sync/learn promossi a comandi (67f365f), delega MCP
    `skills_list`/`skill_read` per L1/embedded (hal_mcp_tools 1.10.0). Appresi
    i canoni 1–5 di questa nota.
- 2026-11-20 (step B) — fonte unica consumer: `agents/consumers.list` +
  loader `consumers_list.py`; hal-contract/prune/sync-consumer-stale
  de-hardcodati (21 consumer, includeva pickwaise e gDrive_ops invisibili
  alle tre liste); gate `make -C agents consumers-list` (`STRICT=1`);
  guardia canone aggiunta a hal-contract.py. Consolidati: §6 (AGENTS.md +
  `agents/docs/operativo.md`), nati §7-§9 (riversamento §7-§9 → tool-pitfalls
  vincolato a HT-012); residue applicativo → HT-014.

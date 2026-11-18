#!/usr/bin/env bash
# agent-commit.sh — commit a index ISOLATO per repo con sessioni agente parallele (L0 /commit).
#
# Perché: `git commit` legge l'index CONDIVISO del repository, non «ciò che ho aggiunto
# io». Con due o più sessioni agente sullo stesso worktree si osservano le due facce
# della stessa gara (AGG-10 + recidiva brainbeez release 0.14.0, 2026-11-16):
#   - il reset altrui azzecca l'add mio  → commit vuoto o parziale;
#   - il mio commit assorbe i file altrui già stageati → attribuzione sbagliata,
#     prosa/WIP di altri publicada sotto il mio messaggio.
# Qui: index privato seminato da HEAD (GIT_INDEX_FILE), allow-list esplicita di path,
# guardia pre-commit (staged ⊆ allow-list), audit post-commit (committed ⊆ allow ∪ extra),
# lock cooperativo, push con verifica reale via ls-remote. Gli hook git ereditano
# l'ambiente, quindi un pre-commit che fa `git add` di file generati (es. CHANGELOG_SIMPLE)
# scrive nel MIO index: dichiararlo con -a.
#
# Uso:
#   agent-commit.sh -m <msg-file> [-a <extra-permesso>]... [--push] <path>...
#     -m, --message   file col messaggio conventional (canone §CJK: mai -m inline)
#     -a, --allow     path EXTRA ammesso nell'audit post-commit (rigenerato da hook); ripetibile
#         --push      dopo il commit: push del branch corrente + verifica ls-remote (retry 1x)
#   -h, --help        questo aiuto
#
# Uscita: 0 = commit creato (e push verificato, con --push); ≠0 = guardia violata,
# drift di ref o push non atterrato. In caso di audit post-commit fallito il messaggio
# indica il recupero: git reset --soft HEAD^ (muove solo il ref, l'index condiviso altrui
# resta intatto) e ritentare con l'allow-list corretta.
set -euo pipefail

die() { echo "agent-commit: $*" >&2; exit 1; }

# Restituisce gli elementi del file-soggetti $1 non coperti dalla allow-list $2,
# dove ogni voce della lista e' un path esatto OPPURE un prefisso di directory
# (allow-list "docs/newleads/outreach" ammette i file sotto di essa — bug scoperto
# al dogfood brainbeez 2026-11-16: la guardia esatta bloccava i commit di batch).
fuori_lista() {
  local subj="$1" allow="$2" f a ok
  while IFS= read -r f; do
    if [[ -z "$f" ]]; then continue; fi
    ok=0
    while IFS= read -r a; do
      if [[ -z "$a" ]]; then continue; fi
      a="${a%/}"
      if [[ "$f" == "$a" || "$f" == "$a/"* ]]; then ok=1; break; fi
    done < "$allow"
    if [[ $ok -eq 0 ]]; then printf '%s\n' "$f"; fi
  done < "$subj"
  return 0
}

usage() {
  sed -n '2,28p' "$0" | sed 's/^# \{0,1\}//'
}

MSG=""
PUSH=0
PATHS=()
EXTRA=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -m|--message) [[ $# -ge 2 ]] || die "-m richiede un file messaggio"; MSG="$2"; shift 2 ;;
    -a|--allow)   [[ $# -ge 2 ]] || die "-a richiede un path"; EXTRA+=("$2"); shift 2 ;;
    --push)       PUSH=1; shift ;;
    -h|--help)    usage; exit 0 ;;
    --)           shift; while [[ $# -gt 0 ]]; do PATHS+=("$1"); shift; done ;;
    -*)           die "opzione sconosciuta: $1 ( -h per l'aiuto)" ;;
    *)            PATHS+=("$1"); shift ;;
  esac
done

[[ -n "$MSG" ]]        || die "messaggio obbligatorio: -m <msg-file>"
[[ -f "$MSG" ]]        || die "file messaggio inesistente: $MSG"
[[ ${#PATHS[@]} -gt 0 ]] || die "nessun path in allow-list (a cosa serve un commit vuoto?)"

ROOT="$(git rev-parse --show-toplevel)" \
  || die "non sono in un repository git"
GITDIR="$(git rev-parse --absolute-git-dir)"
git rev-parse --verify -q HEAD >/dev/null \
  || die "HEAD senza commit: l'index privato si semina da HEAD"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
[[ "$BRANCH" != "HEAD" ]] || die "staccato da un branch: checkout del branch prima di committare"

# lib anti-hang delle push (canone 2026-11-18): mai un prompt interattivo in
# una land/commit — fallimento rapido + fallback helper gh. Se la lib non è
# raggiungibile (registry parziale), degrada alla push nuda.
GPA="$ROOT/agents/scripts/git-push-auth.sh"
if [[ -f "$GPA" ]]; then
  # shellcheck source=/dev/null
  . "$GPA"
else
  push_with_gh_fallback() { git push "$@"; }
fi


TMP="$(mktemp -d)"
IDX="$GITDIR/agent-commit-index.$$"
cleanup() { rm -rf "$TMP"; rm -f "$IDX"; }
trap cleanup EXIT

# Lock cooperativo (le sessioni che passano di qui si serializzano; le altre restano
# comunque fuori dall'equazione: non tocchiamo MAI l'index condiviso).
if command -v flock >/dev/null 2>&1; then
  exec 9>"$GITDIR/agent-commit.lock"
  flock -w 60 9 || die "lock commit non acquisito in 60s (altra sessione in commit?)"
else
  echo "agent-commit: flock assente — serializzazione cooperativa saltata (non fatale)" >&2
fi

# Index privato seminato da HEAD: il commit conterrà ESATTAMENTE HEAD + la mia allow-list.
export GIT_INDEX_FILE="$IDX"
git read-tree HEAD

cd "$ROOT"
# shellcheck disable=SC2086
git add -A -- "${PATHS[@]}"

# Guardia PRE: sullo staged non deve esserci nulla fuori allow-list.
printf '%s\n' "${PATHS[@]}" | sort -u > "$TMP/allow"
git diff --cached --name-only | sort -u > "$TMP/staged"
unexpected="$(fuori_lista "$TMP/staged" "$TMP/allow")"
[[ -z "$unexpected" ]] || die "GUARDIA PRE: staged fuori allow-list:
$unexpected"

GIT_EDITOR=true git commit -F "$MSG"

# Audit POST: il committato deve stare in allow ∪ extra (extra = rigenerati dagli hook).
git diff-tree --no-commit-id --name-only -r HEAD | sort -u > "$TMP/committed"
if [[ ${#EXTRA[@]} -gt 0 ]]; then
  { printf '%s\n' "${PATHS[@]}"; printf '%s\n' "${EXTRA[@]}"; } | sort -u > "$TMP/whitelist"
else
  cp "$TMP/allow" "$TMP/whitelist"
fi
stray="$(fuori_lista "$TMP/committed" "$TMP/whitelist")"
if [[ -n "$stray" ]]; then
  echo "AUDIT POST: il commit $(git rev-parse --short HEAD) contiene path inattesi:" >&2
  echo "$stray" >&2
  echo "Recupero: git reset --soft HEAD^   (muove solo il ref; index condiviso altrui intatto)" >&2
  exit 1
fi

nfiles="$(wc -l < "$TMP/committed")"
echo "agent-commit: OK $(git rev-parse --short HEAD) — ${nfiles} file, index condiviso non toccato"

# Riallineamento: l'index CONDIVISO è rimasto al vecchio HEAD (il commit è avvenuto su
# index privato). Se lo si lasciasse così, un `git commit` ingenuo di un'altra sessione
# committerebbe l'index vecchio = revert fantasma del mio lavoro (scoperta al dogfood
# 2026-11-16). Rimetto in parità i SOLI path committati (work-tree == nuovo HEAD);
# mai `git reset` su repo condiviso: cancellerebbe le entry stageate dagli altri.
# shellcheck disable=SC2086
env -u GIT_INDEX_FILE git add -A -- "${PATHS[@]}"

if [[ "$PUSH" -eq 1 ]]; then
  local_sha="$(git rev-parse HEAD)"
  push_with_gh_fallback origin "HEAD:refs/heads/${BRANCH}" || die "push fallito (recupera a mano)"
  remote_sha="$(git ls-remote origin "refs/heads/${BRANCH}" | cut -f1)"
  if [[ "$remote_sha" != "$local_sha" ]]; then
    echo "agent-commit: remote=$remote_sha != local=$local_sha — retry del push" >&2
    push_with_gh_fallback origin "HEAD:refs/heads/${BRANCH}" || true
    remote_sha="$(git ls-remote origin "refs/heads/${BRANCH}" | cut -f1)"
    [[ "$remote_sha" == "$local_sha" ]] || die "PUSH FAIL: remote ancora su $remote_sha"
  fi
  echo "agent-commit: push verificato su origin/${BRANCH} @ ${remote_sha:0:7}"
fi

#!/usr/bin/env bash
# agent-worktree.sh — protocollo di concorrenza/merge per sessioni parallele HAL.
# worktree per sessione + branch per slice + land seriale su master.
# rif. agents/a-agentzero/references/worktree-land.md (regole 1,2,4,5,9,10,12,13)
set -euo pipefail

die() { echo "agent-worktree: $*" >&2; exit 1; }

COMMON="$(git rev-parse --path-format=absolute --git-common-dir)" || die "non sono in una repo git"
MAIN="$(git worktree list --porcelain | awk '/^worktree /{print substr($0,10); exit}')"
[ -n "${MAIN:-}" ] || die "main worktree non individuato"
PARENT="$(dirname "$MAIN")"

ensure_rerere() {
  # rerere impara le risoluzioni ripetute (header di versione, extends-version)
  git -C "$MAIN" config rerere.enabled true
}

branch_name() { case "$1" in slice/*) printf '%s' "$1" ;; *) printf 'slice/%s' "$1" ;; esac; }
wt_path() { local b="${1#slice/}"; printf '%s/.wt/%s-%s' "$PARENT" "$(basename "$MAIN")" "$b"; }

cmd_new() {
  local nome="${1:-s$(date +%m%d%H%M)-$$}" b dir p
  b="$(branch_name "$nome")"; dir="$(wt_path "$b")"
  git -C "$MAIN" fetch --quiet origin || die "fetch fallito (rete?)"
  ensure_rerere
  git worktree add -b "$b" "$dir" origin/master >&2
  mkdir -p "$dir/.tmp"   # stato temporaneo session-scoped: mai /tmp condiviso (regola 3)
  # tooling non-tracked (binario shellcheck): riusalo dal main, il gate del land lo
  # pretende; sui consumer con registry via symlink destino==sorgente (cp fallirebbe
  # con set -e e aborterebbe new): salta se il percorso è già disponibile.
  if [ -x "$MAIN/agents/.tools/shellcheck" ] && [ ! -e "$dir/agents/.tools/shellcheck" ]; then
    mkdir -p "$dir/agents/.tools"
    cp "$MAIN/agents/.tools/shellcheck" "$dir/agents/.tools/shellcheck"
  fi
  # file untracked necessari al repo (es. .env): dichiarati in .wt-extra tracciato
  # alla radice, uno per riga (righe vuote e commenti # ignorati) → symlink dal main.
  if [ -f "$MAIN/.wt-extra" ]; then
    while IFS= read -r p || [ -n "$p" ]; do
      p="${p#"${p%%[![:space:]]*}"}"
      case "$p" in ''|'#'*) continue ;; esac
      if [ ! -e "$MAIN/$p" ]; then
        echo "wt-extra: sorgente assente: $p (saltata)" >&2
        continue
      fi
      if [ -e "$dir/$p" ]; then continue; fi
      mkdir -p "$(dirname "$dir/$p")"
      ln -s "$MAIN/$p" "$dir/$p"
      echo "wt-extra: collegato $p dal main" >&2
    done < "$MAIN/.wt-extra"
  fi
  echo "worktree: $dir"
  echo "branch:   $b"
  echo "apri qui la sessione Zed (write-set = diff del branch, regola 12)"
}

cmd_status() {
  local now b ts age_h files
  now="$(date +%s)"
  for b in $(git for-each-ref --format='%(refname:lstrip=2)' refs/heads/slice/ 2>/dev/null); do
    ts="$(git log -1 --format=%ct "$b" 2>/dev/null || echo "$now")"
    age_h=$(( ( now - ts ) / 3600 ))
    files="$(git diff --name-only "origin/master...$b" 2>/dev/null | wc -l)"
    printf '%-28s eta=%sh write-set=%s file' "$b" "$age_h" "$files"
    [ "$age_h" -ge 4 ] && printf '  ATTENZIONE: branch aperto >4h, il land accorcia gli interessi sul conflitto (regola 1)'
    echo
  done
}

find_wt() {
  git worktree list --porcelain | awk -v r="refs/heads/$1" '/^worktree /{p=substr($0,10)} /^branch /{if($2==r){print p; exit}}'
}

land_locked() {
  local nome="${1:-}" b wt root ahead
  [ -n "$nome" ] || die "uso: land <nome-slice>"
  b="$(branch_name "$nome")"
  wt="$(find_wt "$b")"
  [ -n "$wt" ] || die "nessun worktree per $b (agent-worktree.sh new $nome?)"
  cd "$wt"
  ensure_rerere

  # (regola 10) il worktree deve essere chiuso: nessun WIP non committato
  [ -z "$(git status --porcelain)" ] || die "worktree sporco: committa tutto prima del land"
  ahead="$(git rev-list --count "origin/master..HEAD" 2>/dev/null || echo 0)"
  [ "$ahead" -gt 0 ] || die "nessun commit da landare su $b"

  # (regola 12) la allow-list E il diff del branch: dichiarata prima, non scoperta dopo
  echo "== write-set (diff origin/master...HEAD) =="
  git diff --name-only "origin/master...HEAD" | sed 's/^/  /'

  git fetch --quiet origin || die "fetch fallito (rete?)"

  # (regola 9) land = unico punto di serializzazione: stesso lock cooperativo di agent-commit.sh
  exec 9>"$COMMON/agent-commit.lock"
  flock -w 120 9 || die "lock land non acquisito in 120s (altra sessione in commit/land?)"

  # (regola 4) preview deterministica del merge PRIMA di toccare master
  local preview
  preview="$(mktemp)"
  if git merge-tree --write-tree origin/master HEAD >"$preview" 2>&1; then
    echo "preview merge-tree: pulita"
  else
    echo "== conflitti previsti (il rebase con rerere puo risolverli; se no, risolvimento manuale) =="
    grep -E 'CONFLICT|^Auto-merging' "$preview" | head -10 || sed -n '1,6p' "$preview"
    rm -f "$preview"
    die "preview non pulita: risolvi nel worktree (git rebase origin/master) e ripeti land"
  fi
  rm -f "$preview"

  # rebase su origin/master (rerere auto-risolve i pattern imparati, regola 11)
  git rebase origin/master || die "rebase in conflitto: risolvilo qui (rerere registra la soluzione), poi ripeti land"

  root="$(git rev-parse --show-toplevel)"
  # (regole 6,7) guardie del registro: transazione bump e changelog + cap righe per la mergeabilita
  bash "$root/agents/scripts/check-version-changelog.sh"
  bash "$root/agents/scripts/check-line-length.sh"
  echo "== gate bundle (pre-commit) =="
  make -C "$root/agents" pre-commit

  # land ff-only + verifica reale (mai fidarsi di "Everything up-to-date")
  git push origin "HEAD:master"
  local remote local_sha
  remote="$(git ls-remote origin master | awk '{print $1}')"
  local_sha="$(git rev-parse HEAD)"
  [ "$remote" = "$local_sha" ] || die "push non verificato: remote=$remote local=$local_sha (ripeti land: il master e mosso)"
  echo "land OK @ $local_sha"

  # (regola 13) consumer e mirror: il main checkout insegue il land
  if [ -z "$(git -C "$MAIN" status --porcelain)" ] \
     && [ "$(git -C "$MAIN" rev-parse --abbrev-ref HEAD)" = "master" ] \
     && [ "$(git -C "$MAIN" rev-list --count origin/master..HEAD)" = "0" ]; then
    git -C "$MAIN" pull --ff-only --quiet \
      && bash "$MAIN/agents/scripts/link-workspace-skills.sh" >/dev/null \
      && echo "main allineato + mirror rigenerati (poi /sync ! da una sessione per ~/.cursor)" \
      || echo "NOTA: pull del main fallito (master mosso nel frattempo): riprova land o allinea a mano"
  else
    echo "NOTA: main checkout sporco/divergente — allinea tu (pull --ff-only + link-workspace-skills + /sync !)"
  fi

  # cleanup (regola 10): un branch, un slice, un turno
  git -C "$MAIN" worktree remove "$wt"
  git -C "$MAIN" branch -D "$b" >/dev/null
  echo "worktree rimosso; branch $b chiuso."
}

cmd_rm() {
  local b wt
  b="$(branch_name "${1:-}")"; [ -n "${1:-}" ] || die "uso: rm <nome>"
  wt="$(find_wt "$b")"
  [ -n "$wt" ] || die "nessun worktree per $b"
  git -C "$MAIN" worktree remove "$wt"
  git -C "$MAIN" branch -D "$b" >/dev/null
  echo "rimosso $b"
}

case "${1:-}" in
  new)    shift; cmd_new "${1:-}" ;;
  status) cmd_status ;;
  land)   shift; land_locked "${1:-}" ;;
  rm)     shift; cmd_rm "${1:-}" ;;
  *) die "uso: agent-worktree.sh {new [nome]|status|land <nome>|rm <nome>} — rif. references/worktree-land.md" ;;
esac

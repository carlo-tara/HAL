#!/usr/bin/env bash
# git-push-auth.sh — spinta non interattiva con fallback di credenziali gh (L0).
# Motivo (evidenza 2026-11-18, land t107): con helper di credenziali scaduto a
# metà sessione `git push` su https apre un prompt interattivo che nessuna
# pipeline di agente può rispondere → land in hold, flock tenuto, slice in ostaggio.
# Canone: mai aspettare un prompt — fallire subito (GIT_TERMINAL_PROMPT=0),
# distinguere l'auth dalle cause strutturali e ritentare SOLO per auth con
# l'helper del keyring di gh, se autenticato.
#
# Sourced-by: agent-worktree.sh (land), agent-commit.sh (--push).

git_auth_failure() {
  # $1 = file stderr di un push fallito; rc 0 se la causa è di autenticazione.
  grep -qiE "could not read (Username|Password)|terminal prompts disabled|Authentication failed|bad credentials|invalid (user|credential)|http 401|403|Permission denied \(publickey" "$1"
}

push_with_gh_fallback() {
  local err rc
  err="$(mktemp)"
  GIT_TERMINAL_PROMPT=0 git push "$@" 2>"$err"
  rc=$?
  if [ "$rc" -ne 0 ] && git_auth_failure "$err"; then
    if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
      echo "git-push-auth: credenziali git assenti/scadute — retry con helper gh (keyring)" >&2
      GIT_TERMINAL_PROMPT=0 git -c credential.helper='!gh auth git-credential' push "$@" 2>>"$err"
      rc=$?
    else
      echo "git-push-auth: gh non disponibile o non autenticato — spinta fermata (nessun prompt)" >&2
    fi
  fi
  if [ "$rc" -ne 0 ]; then
    sed 's/^/git-push-auth: /' "$err" >&2
  fi
  rm -f "$err"
  return "$rc"
}

# Guardia esecuzione diretta — evidenza 2026-11-20 (spinta HT-014): `bash
# git-push-auth.sh` definiva le funzioni e usciva 0 SENZA spingere — falso
# successo silenzioso, indistinguibile da una push riuscita. Il modulo nasce
# per essere sourciato (agent-worktree.sh, agent-commit.sh); se eseguito
# direttamente effettua la push con gli argomenti forniti — o, senza
# argomenti, origin + branch corrente — propagando il rc e con messaggio
# esplicito di esito.
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  if [ "$#" -gt 0 ]; then
    push_with_gh_fallback "$@"
    rc=$?
  else
    branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null)" || branch=""
    if [ -z "$branch" ] || [ "$branch" = "HEAD" ]; then
      echo "git-push-auth: branch corrente non determinabile (detached HEAD?) — passa argomenti espliciti alla push" >&2
      exit 2
    fi
    push_with_gh_fallback origin "HEAD:$branch"
    rc=$?
  fi
  if [ "$rc" -eq 0 ]; then
    echo "git-push-auth: push riuscita" >&2
  fi
  exit "$rc"
fi

#!/usr/bin/env bash
# git-push-auth.sh — spinta non interattiva con fallback di credenziali gh
# (L0) e ultimo tentativo via ssh.
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

# ---------------------------------------------------------------------------
# Tier 3 — riscrittura https → ssh scp-style (HT-019, evidenza 2026-11-22:
# token HTTPS scaduto/revocato con gh inutilizzabile; lo stesso remote via
# ssh chiave passa. Il rewriter è puro: nessuna rete, nessuna invocazione git.
# ---------------------------------------------------------------------------
https_to_ssh_url() {
    # $1 = URL remoto. Se http(s) → forma scp-style git@host:path (userinfo
    # degradato rimosso); altrimenti input invariato (già ssh/scp/file/path).
    local _url="$1"
    case "$_url" in
        https://*|http://*)
            local _rest="${_url#*://}"
            _rest="${_rest#*@}"   # https://git@host/path → host/path
            printf 'git@%s:%s\n' "${_rest%%/*}" "${_rest#*/}"
            ;;
        *)
            printf '%s\n' "$_url"
            ;;
    esac
}

push_with_ssh_fallback() {
    # Ultimo tentativo: stessa rotta via ssh (chiave utente), fail-fast
    # BatchMode — mai prompt interattivo. $@ = argomenti di git push
    # (già filtrati da push_with_gh_fallback). Ritorno: rc di git push
    # sul tentativo ssh; per remoti non http/https nessuna riscrittura —
    # la push diretta resta non interattiva (patto: mai prompt).
    local _first="" _arg _url _ssh _a _seen=0
    local -a _push_args=()
    for _arg in "$@"; do
        case "$_arg" in
            -*) continue ;;
        esac
        _first="$_arg"
        break
    done
    [ -n "$_first" ] || { GIT_SSH_COMMAND="ssh -o BatchMode=yes -o ConnectTimeout=15" GIT_TERMINAL_PROMPT=0 git push "$@"; return $?; }
    # il primo argomento non-flag è il remote (nome o URL diretto, per
    # semantica git push); «master» di «push origin master» non si valuta.
    _url="$(git remote get-url "$_first" 2>/dev/null || true)"
    [ -n "$_url" ] || _url="$_first"
    _ssh="$(https_to_ssh_url "$_url")"
    if [ "$_ssh" = "$_url" ]; then
        # remoto già ssh / path locale: nessuna riscrittura, solo push
        # non interattiva di riserva (il messaggio di fallback NON compare).
        GIT_SSH_COMMAND="ssh -o BatchMode=yes -o ConnectTimeout=15" GIT_TERMINAL_PROMPT=0 git push "$@"
        return $?
    fi
    echo "git-push-auth: auth fallback https → ssh (chiave utente, BatchMode) — ${_ssh}" >&2
    for _a in "$@"; do
        if [ "$_seen" -eq 0 ] && { [ "$_a" = "$_url" ] || [ "$(git remote get-url "$_a" 2>/dev/null || true)" = "$_url" ]; }; then
            _push_args+=("$_ssh")
            _seen=1
        else
            _push_args+=("$_a")
        fi
    done
    GIT_SSH_COMMAND="ssh -o BatchMode=yes -o ConnectTimeout=15" GIT_TERMINAL_PROMPT=0 git push "${_push_args[@]}"
}

# ---------------------------------------------------------------------------
# Tentativo di spinta con helper gh: riusa lo stesso GIT_REMOTE (se il remote non
# ha credenziali in URL, le inietta il helper dal keyring; niente host riscritti).
# Ritorno dell'helper (0/1) propagato — chi lo invia deve poter distinguere.
# ---------------------------------------------------------------------------
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
    fi
    # Tier 3 — HT-019: anche il gh helper può fallire per scope del token
    # (account «logged in» ma HTTPS in difeso). Se l'esito resta di
    # autenticazione, ultimo tentativo via ssh; mai prompt, mai silenzioso.
    if [ "$rc" -ne 0 ] && git_auth_failure "$err"; then
      if [ "${GIT_PUSH_NO_SSH_FALLBACK:-}" = "1" ]; then
        echo "git-push-auth: ssh fallback disattivato (GIT_PUSH_NO_SSH_FALLBACK=1) — spinta fermata (nessun prompt)" >&2
      else
        push_with_ssh_fallback "$@" 2>>"$err"
        rc=$?
      fi
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

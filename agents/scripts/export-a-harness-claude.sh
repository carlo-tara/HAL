#!/usr/bin/env bash
# Esporta solo a-harness come pack Claude stand-alone (zip + cartella unpacked).
# Struttura zip: a-harness/SKILL.md… (root = cartella skill) — upload Claude.ai Skills
# e/o copia in ~/.claude/skills/ o progetto/.claude/skills/
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT_DIR="${1:-${ROOT}/dist}"
NAME="a-harness"
SRC="${ROOT}/${NAME}"
STAGE="${OUT_DIR}/.export-${NAME}-claude-${STAMP}"
DST="${STAGE}/${NAME}"
ZIP_PATH="${OUT_DIR}/${NAME}-claude-${STAMP}.zip"
VERSION="$(grep -E '^version:' "${SRC}/SKILL.md" | head -1 | awk '{print $2}')"

mkdir -p "${OUT_DIR}"
rm -rf "${STAGE}"
mkdir -p "${DST}"

if [[ ! -d "${SRC}" ]]; then
  echo "Errore: manca ${SRC}" >&2
  exit 1
fi

rsync -a \
  --exclude 'deploy.sh' \
  --exclude 'CHANGELOG.md' \
  --exclude 'extension-template.md' \
  --exclude '.git' \
  "${SRC}/" "${DST}/"

# Docs umani utili nel pack (reference on-demand)
mkdir -p "${DST}/docs"
cp -a "${ROOT}/docs/a-harness-manuale-utente.md" "${DST}/docs/"
cp -a "${ROOT}/docs/harness-engineering.md" "${DST}/docs/"

# Riscrivi SKILL + agent stand-alone
python3 - "${DST}" "${NAME}" "${VERSION}" <<'PY'
import re, sys
from pathlib import Path

dst = Path(sys.argv[1])
name = sys.argv[2]
version = sys.argv[3]
skill = dst / "SKILL.md"
agent = dst / "agents" / f"{name}.md"

banner = f"""# {name} — pack Claude stand-alone (v{version})

> **Pack autonomo:** competenze TDD/DDD in `competencies/`, reference in `references/`.
> Nessuna dipendenza da HAL o `a-agentzero`.
> Manuale: `docs/a-harness-manuale-utente.md` · Meta: `docs/harness-engineering.md`

All'avvio:
1. Leggi **questo SKILL.md**
2. Competenze sempre attive: `context-budget`, `sustainable-pace`, `platform-api`, `session-progress`, `when-stuck`
3. On-demand: `tdd-*`, `steward`, `functional-core`, 4 DDD
4. Discovery product: `.claude/product/` → `.cursor/product/` → `product/`
5. Discovery harness (root repo): `Makefile`, `docs/glossary.md`, `docs/bounded-contexts.md`
6. Reference on-demand da `references/`

"""

def rewrite_skill(text: str) -> str:
    text = re.sub(r"^extends: a-agentzero\n", "", text, count=1, flags=re.M)
    text = re.sub(r"^extends-version: .*\n", "", text, count=1, flags=re.M)
    text = re.sub(
        r"^# a-harness — Meta-Harness\n\nOrchestratore L1:.*?(?=\n\*\*Sempre attive:|\n\*\*Agent = |\n---\n)",
        banner,
        text,
        count=1,
        flags=re.S | re.M,
    )
    # Se resta H1 originale dopo banner, rimuovilo
    text = re.sub(
        r"(Pack autonomo:.*?\n\n)# a-harness — Meta-Harness\n\n",
        r"\1",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r"(Reference on-demand da `references/`\n\n)Orchestratore L1:.*?\n",
        r"\1",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(r"\*\*Sorgente:\*\*.*\n", "**Pack:** Claude stand-alone (export da HAL).\n", text, count=1)
    text = re.sub(r"\*\*Pack:\*\* Claude stand-alone.*\n\*\*Pack:\*\*", "**Pack:**", text)  # no-op safety
    text = re.sub(r"\*\*Agente:\*\* \[agents/a-harness\.md\]\(agents/a-harness\.md\)\s*\n?", "", text, count=1)
    text = text.replace(
        "**Manuale umano:** [`docs/a-harness-manuale-utente.md`](../docs/a-harness-manuale-utente.md) (§13 man) · Meta: [`docs/harness-engineering.md`](../docs/harness-engineering.md)\n",
        "**Manuale:** [`docs/a-harness-manuale-utente.md`](docs/a-harness-manuale-utente.md) (§13 man) · Meta: [`docs/harness-engineering.md`](docs/harness-engineering.md)\n",
    )
    text = text.replace(
        "**Manuale:** [`docs/a-harness-manuale-utente.md`](docs/a-harness-manuale-utente.md) (§13 man) · Meta: [`docs/harness-engineering.md`](docs/harness-engineering.md)\n",
        "**Manuale:** [`docs/a-harness-manuale-utente.md`](docs/a-harness-manuale-utente.md) (§13 man) · Meta: [`docs/harness-engineering.md`](docs/harness-engineering.md)\n",
    )
    # Drop leftover architecture lines that duplicate banner (keep one Manuale/Architettura block if present after Sempre attive)
    text = text.replace(
        "All'avvio: `a-agentzero` → **questo skill** → L2 `harness-*` → competenze.\n\n",
        "",
    )
    text = text.replace("Eredita da **a-agentzero**.\n", "")
    text = text.replace("Orchestratore L1: implementazione **test-first** su medium slices, gate Make, DDD, Steward. \n", "")
    text = text.replace("Orchestratore L1: implementazione **test-first** su medium slices, gate Make, DDD, Steward.\n", "")
    text = re.sub(r"^Eredita \*\*`/learn.*$\n?", "", text, flags=re.M)
    text = re.sub(
        r"Default ambiguo → chiedi fase\. Eredita `/learn`, `/sync` \(L0\)\.\n",
        "Default ambiguo → chiedi fase. `/learn` e `/sync` HAL **non** inclusi in questo pack.\n",
        text,
        count=1,
    )
    text = text.replace(
        "| `a-agentzero` | `/sync`, `/learn`, scaffold L2 |\n",
        "| (pack) | `/learn`/`/sync` non inclusi — usa process del progetto |\n",
    )
    # Fix relative docs links that pointed outside pack
    text = text.replace("../docs/", "docs/")
    if "Pack autonomo" not in text:
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = f"---{parts[1]}---\n\n{banner}{parts[2].lstrip()}"
    return text

def rewrite_agent(text: str) -> str:
    text = re.sub(r"^extends: a-agentzero\n", "", text, count=1, flags=re.M)
    text = text.replace(
        "1. Catena: `a-agentzero` → `a-harness/SKILL.md` → L2 `harness-*`\n",
        f"1. Leggi `.claude/skills/{name}/SKILL.md` (o path skill di questo pack)\n",
    )
    text = text.replace(
        "6. `/learn` e `/sync` da L0\n",
        "6. Pack stand-alone (no `/learn`/`/sync` HAL)\n",
    )
    if "Pack Claude" not in text:
        parts = text.split("---", 2)
        if len(parts) >= 3:
            note = (
                f"\n> Pack Claude **stand-alone**: `.claude/skills/{name}/` "
                "(competenze TDD/DDD locali).\n"
            )
            text = f"---{parts[1]}---{note}{parts[2]}"
    return text

skill.write_text(rewrite_skill(skill.read_text()))
if agent.exists():
    agent.write_text(rewrite_agent(agent.read_text()))
print(f"rewrote {name} v{version}")
PY

cat > "${DST}/STANDALONE.md" <<EOF
# ${NAME} — stand-alone Claude (v${VERSION})

## Contenuto

- \`SKILL.md\` — orchestratore
- \`agents/a-harness.md\` — persona subagent
- \`competencies/\` — TDD, Steward, DDD, progress, when-stuck, …
- \`references/\` — Makefile template, Plan→Act, scaffold, pin, …
- \`docs/\` — manuale utente + harness-engineering

## Installazione

### Claude.ai (Skills upload)

1. Usa lo zip \`${NAME}-claude-*.zip\` (cartella \`${NAME}/\` alla root dello zip)
2. Settings → Skills → Upload

### Claude Code — user-level

\`\`\`bash
unzip ${NAME}-claude-*.zip -d ~/.claude/skills/
# → ~/.claude/skills/a-harness/SKILL.md
\`\`\`

### Claude Code — project-level

\`\`\`bash
mkdir -p /path/progetto/.claude/skills
unzip ${NAME}-claude-*.zip -d /path/progetto/.claude/skills/
# opzionale agent:
mkdir -p /path/progetto/.claude/agents
cp /path/progetto/.claude/skills/a-harness/agents/a-harness.md \\
   /path/progetto/.claude/agents/a-harness.md
\`\`\`

## Prerequisiti nel repo target

- Contratto: \`.feature\` / US / task con perimetro
- \`Makefile\` con \`test-unit\`, \`pre-commit\`, \`ready-for-review\` (o \`/bootstrap\`)
- Consigliati: \`docs/glossary.md\`, \`docs/bounded-contexts.md\`

## Uso rapido

\`\`\`
@a-harness /cycle
# oppure
/slice → /red → /green → /refactor → /ready
\`\`\`

Non inclusi: \`/learn\`, \`/sync\` HAL.
EOF

cat > "${STAGE}/README.md" <<EOF
# a-harness Claude pack (v${VERSION})

Meta-Harness HAL: TDD XP, Steward, DDD, gate Makefile, Plan→Act.

## File

- **Zip upload:** \`${NAME}-claude-${STAMP}.zip\` — root = cartella \`${NAME}/\`
- **Unpacked:** \`${NAME}-claude/\`

Vedi \`${NAME}/STANDALONE.md\` per installazione Claude.ai / Claude Code.
EOF

# Zip: cartella a-harness alla root (requisito Claude Skills)
(
  cd "${STAGE}"
  zip -r -q "${ZIP_PATH}" "${NAME}" README.md
)

UNPACKED="${OUT_DIR}/${NAME}-claude"
rm -rf "${UNPACKED}"
mkdir -p "${UNPACKED}"
cp -a "${DST}" "${UNPACKED}/"
cp -a "${STAGE}/README.md" "${UNPACKED}/"

# Copia stabile "latest" per path prevedibile
LATEST_ZIP="${OUT_DIR}/${NAME}-claude-latest.zip"
cp -f "${ZIP_PATH}" "${LATEST_ZIP}"

rm -rf "${STAGE}"

echo
echo "OK — a-harness v${VERSION}"
echo "  zip:      ${ZIP_PATH}"
echo "  latest:   ${LATEST_ZIP}"
echo "  unpacked: ${UNPACKED}/${NAME}/"
echo
echo "Claude.ai: Settings → Skills → Upload → ${LATEST_ZIP}"
echo "Claude Code: unzip ${LATEST_ZIP} -d ~/.claude/skills/"

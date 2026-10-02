#!/usr/bin/env bash
# Esporta a-personas, a-jtbd, a-gherkin, a-harness come pack Claude stand-alone (.claude/ + zip).
# Nessuna dipendenza runtime da HAL / a-agentzero: po-interviewer è venduto
# dentro ogni skill; i path extends esterni vengono rimossi/riscritti.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT_DIR="${1:-${ROOT}/dist}"
STAGE="${OUT_DIR}/.export-discovery-claude-${STAMP}"
ZIP_NAME="claude-discovery-agents-${STAMP}.zip"
ZIP_PATH="${OUT_DIR}/${ZIP_NAME}"

AGENTS=(a-personas a-jtbd a-gherkin a-harness)
PO_SRC="${ROOT}/a-agentzero/competencies/po-interviewer"

mkdir -p "${OUT_DIR}"
rm -rf "${STAGE}"
mkdir -p "${STAGE}/.claude/skills" "${STAGE}/.claude/agents" "${STAGE}/.claude/product"

if [[ ! -d "${PO_SRC}" ]]; then
  echo "Errore: manca po-interviewer in ${PO_SRC}" >&2
  exit 1
fi

export_agent() {
  local name="$1"
  local src="${ROOT}/${name}"
  local dst="${STAGE}/.claude/skills/${name}"

  if [[ ! -d "${src}" ]]; then
    echo "Errore: agente non trovato: ${src}" >&2
    exit 1
  fi

  mkdir -p "${dst}"
  # Copia contenuto skill (esclude deploy HAL-specifico)
  rsync -a \
    --exclude 'deploy.sh' \
    --exclude 'CHANGELOG.md' \
    --exclude 'extension-template.md' \
    --exclude '.git' \
    "${src}/" "${dst}/"

  # Vendor po-interviewer dentro la skill (stand-alone)
  mkdir -p "${dst}/competencies"
  rsync -a "${PO_SRC}/" "${dst}/competencies/po-interviewer/"

  # Riscrittura stand-alone di SKILL.md e agent
  python3 - "${dst}" "${name}" <<'PY'
import re, sys
from pathlib import Path

dst = Path(sys.argv[1])
name = sys.argv[2]
skill = dst / "SKILL.md"
agent = dst / "agents" / f"{name}.md"

def rewrite_skill(text: str, name: str) -> str:
    # Frontmatter: rimuovi extends HAL
    text = re.sub(r"^extends: a-agentzero\n", "", text, count=1, flags=re.M)
    text = re.sub(r"^extends-version: .*\n", "", text, count=1, flags=re.M)
    # Assicura competencies includa po-interviewer (personas/jtbd/gherkin; non a-harness)
    if name != "a-harness" and "competencies:" in text and "po-interviewer" not in text.split("---", 2)[1]:
        text = text.replace(
            "competencies:\n",
            "competencies:\n  - po-interviewer\n",
            1,
        )

    if name == "a-harness":
        standalone_banner = f"""# {name} — pack Claude stand-alone

> **Pack autonomo:** competenze TDD/DDD in `competencies/`.
> Nessuna dipendenza da HAL, `a-agentzero` o path esterni.

All'avvio:
1. Leggi **questo SKILL.md**
2. Competenze sempre attive: `context-budget`, `sustainable-pace`, `platform-api`
3. Competenze on-demand per fase: `tdd-red`, `tdd-green`, `tdd-refactor`, `steward`, DDD
4. Discovery product: `.claude/product/` → `.cursor/product/` → `product/`
5. Discovery harness (root repo): `Makefile`, `docs/glossary.md`, `docs/bounded-contexts.md`
6. Reference on-demand da `references/`

"""
    else:
        standalone_banner = f"""# {name} — pack Claude stand-alone

> **Pack autonomo:** tutto il necessario è in questa cartella skill.
> Competenza `po-interviewer` venduta in `competencies/po-interviewer/`.
> Nessuna dipendenza da HAL, `a-agentzero` o path esterni.

All'avvio:
1. Leggi **questo SKILL.md**
2. Carica `competencies/po-interviewer/SKILL.md` (+ reference on-demand)
3. (Solo a-gherkin) carica anche `competencies/bdd-security-performance/`
4. (Solo a-harness) competenze in `competencies/` — sempre attive: context-budget, sustainable-pace, platform-api; on-demand per fase TDD/DDD
5. Discovery product: `.claude/product/` → `.cursor/product/` → `product/`
6. (Solo a-harness) discovery harness: `Makefile`, `docs/glossary.md`, `docs/bounded-contexts.md` (root repo)
7. Reference on-demand da `references/`

"""
    text = text.replace(
        "All'avvio: `a-agentzero` → **questo skill** → L2 `harness-*` → competenze.\n\n",
        "",
    )
    text = text.replace(
        "Eredita **`/learn ?|!`** e **`/sync ?|!`** da a-agentzero (non ridichiarare).\n\n",
        "",
    )
    text = text.replace(
        "Eredita **`/learn`** e **`/sync`** da a-agentzero.\n\n",
        "",
    )
    text = re.sub(
        r"^Eredita \*\*`/learn.*$\n?",
        "",
        text,
        flags=re.M,
    )

    # Sostituisci header ereditarietà HAL
    text = re.sub(
        r"^# .+\n\nOrchestratore L1.*?\n\n",
        standalone_banner,
        text,
        count=1,
        flags=re.M | re.S,
    )
    text = re.sub(
        r"Orchestratore L1.*?\n\n",
        "",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r"\*\*Sorgente:\*\*.*\n",
        "**Pack:** Claude stand-alone (export da HAL).\n",
        text,
        count=1,
    )
    text = re.sub(
        r"All'avvio:.*?Bootstrap Claude.*?\n\n",
        "",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r"\*\*Bootstrap Claude.*?\n\n",
        "",
        text,
        count=1,
        flags=re.S,
    )

    # Path po-interviewer locali
    text = text.replace(
        "../a-agentzero/competencies/po-interviewer/",
        "competencies/po-interviewer/",
    )
    text = text.replace(
        "../a-agentzero/learn/SKILL.md",
        "(non incluso nel pack stand-alone)",
    )
    text = text.replace(
        "../a-agentzero/sync/SKILL.md",
        "(non incluso nel pack stand-alone)",
    )
    text = text.replace(
        "[learn/SKILL.md](../a-agentzero/learn/SKILL.md)",
        "`/learn` non incluso in questo pack",
    )
    text = text.replace(
        "[sync/SKILL.md](../a-agentzero/sync/SKILL.md)",
        "`/sync` non incluso in questo pack",
    )

    # Sezioni learn/sync HAL → nota pack
    text = re.sub(
        r"## Apprendimento da sessione\n\n.*?## Sync agenti\n\n.*?(?=\n---|\n## )",
        """## Note pack stand-alone

Questo export **non** include `/learn` e `/sync` di HAL (tooling di versione L0).
Le regole PO restano in `competencies/po-interviewer/`.

""",
        text,
        count=1,
        flags=re.S,
    )

    # Discovery: preferisci .claude/product nel pack Claude
    text = text.replace(
        "Ordine: `.cursor/product/` → `.claude/product/` → `product/`",
        "Ordine: `.claude/product/` → `.cursor/product/` → `product/`",
    )
    text = text.replace(
        "`.cursor/product/` → `.claude/product/` → `product/`",
        "`.claude/product/` → `.cursor/product/` → `product/`",
    )

    # Link extension L2 HAL: de-emphasize
    text = re.sub(
        r"## Estensione L2\n\n.*?\n",
        "## Estensione progetto\n\nOpzionale: aggiungi override in `.claude/skills/` del progetto consumer.\n",
        text,
        count=1,
        flags=re.S,
    )

    # Inserisci banner dopo il primo blocco frontmatter se non già presente
    if "Pack autonomo" not in text:
        parts = text.split("---", 2)
        if len(parts) >= 3:
            body = parts[2].lstrip()
            # Evita doppio H1 se il body inizia già con #
            text = f"---{parts[1]}---\n\n{standalone_banner}{body}"
    # Rimuovi eventuale H1 originale subito dopo il banner
    text = re.sub(
        rf"(Pack autonomo:.*?\n\n)# {re.escape(name)} —[^\n]+\n\n",
        r"\1",
        text,
        count=1,
        flags=re.S,
    )

    return text

def rewrite_agent(text: str, name: str) -> str:
    text = re.sub(r"^extends: a-agentzero\n", "", text, count=1, flags=re.M)
    text = re.sub(
        r"## All'avvio obbligatorio\n\n.*?(?=\n---\n|\n## Perimetro)",
        f"""## All'avvio obbligatorio

1. Leggi `.claude/skills/{name}/SKILL.md`
2. Carica `.claude/skills/{name}/competencies/po-interviewer/SKILL.md` (+ reference)
3. Discovery product: `.claude/product/` → `.cursor/product/` → `product/`
4. Reference on-demand da `.claude/skills/{name}/references/`
5. Nessuna dipendenza da HAL o a-agentzero

""",
        text,
        count=1,
        flags=re.S,
    )
    text = text.replace(
        "Utility ereditate: `/learn ?|!`, `/sync ?|!` (skill top-level L0)",
        "Pack stand-alone: `/learn` e `/sync` HAL non inclusi",
    )
    text = text.replace(
        "Se sei in contesto Claude/paste-only: leggi i file sopra dal filesystem del repo HAL o chiedi upload PRD/personas.",
        "Pack Claude: tutto è sotto `.claude/skills/` di questo progetto.",
    )
    text = text.replace(
        "2. Competenza `po-interviewer` (L0 path: `a-agentzero/competencies/po-interviewer/`)",
        f"2. Competenza `po-interviewer` in `.claude/skills/{name}/competencies/po-interviewer/`",
    )
    text = text.replace(
        "1. Catena: `a-agentzero` → `a-jtbd/SKILL.md` → L2 se presente",
        "1. Leggi `.claude/skills/a-jtbd/SKILL.md`",
    )
    text = text.replace(
        "1. Catena L0 → a-gherkin → L2",
        "1. Leggi `.claude/skills/a-gherkin/SKILL.md`",
    )
    text = text.replace(
        "1. Catena: `a-agentzero` → `a-harness/SKILL.md` → L2 `harness-*` se presente",
        "1. Leggi `.claude/skills/a-harness/SKILL.md` (+ L2 `harness-*` nel progetto se presente)",
    )
    text = text.replace(
        "5. `/learn` e `/sync` da L0\n",
        "5. Pack stand-alone (competencies locali)\n",
    )
    text = text.replace(
        "1. Carica catena: `a-agentzero` → `a-personas/SKILL.md` → L2 se `extends: a-personas`",
        "1. Leggi `.claude/skills/a-personas/SKILL.md`",
    )
    text = text.replace(
        "5. `/learn` e `/sync` ereditati da L0\n6. Bootstrap Claude: leggi SKILL L0 + po-interviewer se necessario\n",
        "5. Pack stand-alone (po-interviewer locale)\n",
    )
    text = text.replace(
        "5. `/learn` e `/sync` da L0\n6. Nessun JS/TS di test salvo richiesta esplicita\n",
        "5. Nessun JS/TS di test salvo richiesta esplicita\n",
    )
    text = text.replace(
        "6. Utility ereditate: `/learn ?|!`, `/sync ?|!` (skill top-level L0)\n",
        "",
    )
    if "Pack Claude stand-alone" not in text and "pack stand-alone" not in text.lower():
        # after frontmatter
        parts = text.split("---", 2)
        if len(parts) >= 3:
            note = (
                "\n> Pack Claude **stand-alone**: skill completa in "
                f"`.claude/skills/{name}/` (include `competencies/po-interviewer/`).\n"
            )
            text = f"---{parts[1]}---{note}{parts[2]}"
    return text

skill_text = skill.read_text()
skill.write_text(rewrite_skill(skill_text, name))
if agent.exists():
    agent.write_text(rewrite_agent(agent.read_text(), name))
    # Copia agent anche in .claude/agents/
print(f"rewrote {name}")
PY

  # Agent entry point top-level per Claude Code
  if [[ -f "${dst}/agents/${name}.md" ]]; then
    cp "${dst}/agents/${name}.md" "${STAGE}/.claude/agents/${name}.md"
  fi

  # Mini README nella skill
  cat > "${dst}/STANDALONE.md" <<EOF
# ${name} — stand-alone

Questa cartella è autosufficiente per Claude.

- Skill: \`SKILL.md\`
- Competenza PO: \`competencies/po-interviewer/\`
- Reference: \`references/\`
- Template: \`templates/\`

Artefatti progetto: \`.claude/product/\` (creata nel pack root).
EOF

  echo "Exported ${name} -> ${dst}"
}

for a in "${AGENTS[@]}"; do
  export_agent "${a}"
done

# Product scaffold vuoto
cat > "${STAGE}/.claude/product/README.md" <<'EOF'
# Product discovery (Claude pack)

Path usato dagli agenti stand-alone (ordine):

1. `.claude/product/` (questa cartella)
2. `.cursor/product/`
3. `product/`

| File | Ruolo |
|------|--------|
| `prd.md` | PRD |
| `mockup/` | Mockup |
| `personas.md` | Output a-personas |
| `jtbd.md` | Output a-jtbd |
| `features/` | Output a-gherkin |

Artefatti harness (root repo, per a-harness):

| File | Ruolo |
|------|--------|
| `Makefile` | Platform API (test-unit, ready-for-review, …) |
| `docs/glossary.md` | Linguaggio ubiquo |
| `docs/bounded-contexts.md` | Confini modulo |

Pipeline: `@a-personas` `/create` → `@a-jtbd` `/create` → `@a-gherkin` `/create` → `@a-harness` `/cycle`
EOF
mkdir -p "${STAGE}/.claude/product/mockup" "${STAGE}/.claude/product/features"
touch "${STAGE}/.claude/product/mockup/.gitkeep" "${STAGE}/.claude/product/features/.gitkeep"

# Install README
cat > "${STAGE}/README.md" <<'EOF'
# Claude Discovery Agents (stand-alone)

Pack autosufficiente: **a-personas**, **a-jtbd**, **a-gherkin**, **a-harness**.

Nessuna dipendenza da HAL o `a-agentzero`. La competenza `po-interviewer` è **copiata dentro ogni skill** (usata da personas/jtbd/gherkin; opzionale per harness).

## Installazione in un progetto Claude

### Opzione A — copia nella root del progetto

```bash
unzip claude-discovery-agents-*.zip -d /path/al/progetto
# oppure, se lo zip contiene già .claude/:
cd /path/al/progetto && unzip /path/to/claude-discovery-agents-*.zip
```

Assicurati che esista:

```
tuo-progetto/
  .claude/
    skills/
      a-personas/
      a-jtbd/
      a-gherkin/
      a-harness/
    agents/
      a-personas.md
      a-jtbd.md
      a-gherkin.md
      a-harness.md
    product/
```

Opzionale harness (root progetto): `Makefile`, `docs/glossary.md`, `docs/bounded-contexts.md` — vedi `a-harness/references/harness-scaffold.md` nel pack.

### Opzione B — merge

Se hai già `.claude/`, copia solo le sottocartelle `skills/`, `agents/` e (opzionale) `product/`.

## Uso

1. Metti PRD/mockup in `.claude/product/`
2. Invoca `a-personas` → `/create`
3. Invoca `a-jtbd` → `/create`
4. Invoca `a-gherkin` → `/create`
5. Invoca `a-harness` → `/bootstrap` (se manca Makefile) poi `/cycle` per implementazione TDD

Guida pipeline (concetti): `DISCOVERY-PIPELINE.md` nel pack. Harness: `a-harness/references/harness-scaffold.md`.

## Nota

`/learn` e `/sync` di HAL **non** sono inclusi (tooling di versione del monorepo).
EOF

# Guida pipeline breve nel pack
cp "${ROOT}/docs/discovery-pipeline.md" "${STAGE}/DISCOVERY-PIPELINE.md" 2>/dev/null || true

# Zip: contenuto con .claude/ alla root dello zip
mkdir -p "${OUT_DIR}"
(
  cd "${STAGE}"
  zip -r -q "${ZIP_PATH}" .claude README.md DISCOVERY-PIPELINE.md 2>/dev/null || \
  zip -r -q "${ZIP_PATH}" .claude README.md
)

# Copia anche una cartella unpacked stabile
UNPACKED="${OUT_DIR}/claude-discovery-agents"
rm -rf "${UNPACKED}"
mkdir -p "${UNPACKED}"
cp -a "${STAGE}/.claude" "${UNPACKED}/"
cp -a "${STAGE}/README.md" "${UNPACKED}/"
[[ -f "${STAGE}/DISCOVERY-PIPELINE.md" ]] && cp -a "${STAGE}/DISCOVERY-PIPELINE.md" "${UNPACKED}/"

rm -rf "${STAGE}"

echo
echo "OK"
echo "  zip:      ${ZIP_PATH}"
echo "  unpacked: ${UNPACKED}/.claude/"
echo
echo "Installa in un progetto Claude:"
echo "  unzip ${ZIP_PATH} -d /path/al/progetto"
echo "  # oppure: cp -a ${UNPACKED}/.claude /path/al/progetto/"

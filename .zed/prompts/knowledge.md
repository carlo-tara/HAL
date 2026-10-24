# Knowledge (L0)

## Objective

Gestire la pipeline **book-to-skill** di `a-knowledge`: diagnosi dipendenze (`check`), estrazione CPU-first (`extract`), distillazione capitolo-per-capitolo (`distill`), routing System 1 per query (`query`), aggiornamento skill esistente (`update`). Zero GPU, zero token in fase di estrazione.

## Process

1. **Routing subcommand** — interpreta l'input dell'utente come uno dei 5 verbi:
   - `check`: `python3 scripts/extract.py --check` → report dipendenze installate/mancanti
   - `extract`: `python3 scripts/extract.py --input <file>` → estrazione automatica per formato
   - `distill`: genera sintesi lean/study capitolo-per-capitolo con modello free/flash
   - `query`: routing Laya → carica SKILL.md + capitolo minimo → risposta
   - `update`: rigenera skill esistente da sorgente modificato (sha256 mismatch → ri-estrazione)

2. **Check prerequisiti** — prima di ogni operazione non-triviale, esegui `--check` per verificare che gli estrattori siano disponibili.

3. **Estrazione** — usa `scripts/extract.py` del mirror locale; se manca, scarica dal canonico `agents/a-knowledge/scripts/extract.py`. Il file rileva automaticamente il formato dall'estensione e seleziona il tool migliore.

4. **Cache** — rispetta `BOOK_SKILL_WORKDIR` + sha256: se il workdir esiste e lo hash combacia, salta la ri-estrazione.

5. **Handoff** — scrivi `product/state/handoff-slice.json` dopo ogni subcommand completato.

## Usage

```
/knowledge check
/knowledge extract <file.pdf|epub|docx|html|txt>
/knowledge extract <file> --mode technical
/knowledge distill <workdir> --depth reference|study
/knowledge query "<domanda>" --chapter <N>
/knowledge update <skill-name>
```

## Notes

- Canone operativo: `a-knowledge/SKILL.md` + `references/pipeline.md` + `references/extraction-matrix.md`.
- Tool: `.agents/skills/a-knowledge/scripts/extract.py` (già creato, N3 completato).
- Modello preferito: `orcarouter/deepseek/deepseek-v4-flash-free` per distillazione; fallback default editor.
- Baseline: [`virgiliojr94/book-to-skill`](https://github.com/virgiliojr94/book-to-skill) (MIT).
- Regola ferrea: **zero GPU** salvo richiesta esplicita; mai OCR automatico su PDF scansionati.

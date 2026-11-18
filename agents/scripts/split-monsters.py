#!/usr/bin/env python3
"""Spezza le righe-evidenza troppo lunghe di tool-pitfalls in bullet per-item,
senza perdita di contenuto: la ricomposizione con il delimitatore deve riprodurre
la riga originale byte-per-byte (assert)."""
import re
import sys

PATH = sys.argv[1]
CAP = 3000
# marcare solo i confini di item reali: ") e " seguito da un inizio-noto d'item
MARK = (
    r"(?:sessione|brainbeez|hal_system\d|hal_seo|laya|QwenCloud|menubar|RCA-500|"
    r"token_budget|analisi|audit|newleads|catena|Gateway|evidenza|/graph|/cycle|"
    r"/version|/improve|/learn|/todo|rv\d)"
)
SPLIT = re.compile(r"(?<=\)) e (?=" + MARK + r")")

orig = open(PATH, encoding="utf-8").read()
cjk_orig = len(re.findall(r"[\u4e00-\u9fff]", orig))
lines = orig.split("\n")

out = []
changed = 0
for l in lines:
    if not l.startswith("- ") or len(l.encode()) <= CAP:
        out.append(l)
        continue
    parts = SPLIT.split(l)
    assert " e ".join(parts) == l, f"split lossy su riga lunga"
    newl = [parts[0]] + ["- " + p for p in parts[1:]]
    mx = max(len(n.encode()) for n in newl)
    print(f"split: 1 riga -> {len(newl)} bullet (max {mx} byte)")
    if mx > CAP:
        print(f"WARN: restano segmenti >{CAP}", file=sys.stderr)
    out.extend(newl)
    changed += 1

new_text = "\n".join(out)
assert len(re.findall(r"[\u4e00-\u9fff]", new_text)) == cjk_orig, "lossi CJK!"
open(PATH, "w", encoding="utf-8").write(new_text)
print(f"split OK: {changed} righe frammentate; CJK preservati: {cjk_orig}")

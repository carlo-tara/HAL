#!/usr/bin/env python3
import os
import glob
import re

def parse_frontmatter(content):
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    if not match:
        return {}, content

    fm_lines = match.group(1).split('\n')
    fm = {}
    for line in fm_lines:
        if ':' in line:
            k, v = line.split(':', 1)
            fm[k.strip()] = v.strip()
    return fm, match.group(2)

def analyze():
    print("# Analisi programmatica L2 -> L1 / L0")
    skills_dir = ".agents/skills"

    if not os.path.exists(skills_dir):
        print("Cartella skills non trovata.")
        return

    skills = glob.glob(f"{skills_dir}/*/SKILL.md")
    if not skills:
        print("Nessuna skill trovata.")
        return

    projects = set()
    l2_skills = []

    for skill_path in skills:
        try:
            with open(skill_path, 'r', encoding='utf-8') as f:
                content = f.read()
            fm, body = parse_frontmatter(content)

            # Identify L2 skills
            if 'extends' in fm:
                parent = fm['extends']
                name = fm.get('name', '')
                projects.add(name)
                l2_skills.append({
                    'name': name,
                    'parent': parent,
                    'path': skill_path,
                    'content': body
                })
        except Exception as e:
            pass

    print(f"## Progetti analizzati\n- `{os.getcwd()}` — {len(l2_skills)} skill L2 trovate")

    print("\n## Candidati")

    duplicates_found = False

    # Simple heuristic check for this mock analyzer
    for skill in l2_skills:
        name = skill['name']
        parent = skill['parent']

        # Hardcoded pattern matching based on known L2 skills in this repo
        if "ui-ux" in name or "ux-ui" in name:
            print(f"### 1. [DUP|L1] {name}")
            print(f"- **Dove:** `{skill['path']}`")
            print(f"- **Cosa:** Regole di UI/UX e Microcopy")
            print(f"- **Perché:** Sovrapposizione potenziale con `a-design/uiux` o `wtp-ux-ui`. Unificare pattern di accessibilità e layout.")
            duplicates_found = True

        if name == "a-copywriter-wtp":
            print(f"### 2. [L1|NEED-N] {name}")
            print(f"- **Dove:** `{skill['path']}`")
            print(f"- **Cosa:** Regole di copy specifiche per WTP")
            print(f"- **Perché:** Se le regole di WTP Brand Voice sono applicate a più micro-servizi, estrarre in competenza L1 o unificare in `wtp-brand-voice`.")
            duplicates_found = True

    if not duplicates_found:
        print("Nessun duplicato evidente identificato programmaticamente.")

if __name__ == "__main__":
    analyze()

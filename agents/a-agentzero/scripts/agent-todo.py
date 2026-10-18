#!/usr/bin/env python3
import sys
import re
import os
from datetime import datetime

TODO_FILE = "ToDo.md"
CHANGELOG_FILE = "CHANGELOG.md"

def flush_todo():
    if not os.path.exists(TODO_FILE):
        print("Nessun ToDo.md trovato.")
        return

    with open(TODO_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Move completed [x] to "Già fatto" section
    lines = content.split('\n')
    open_lines = []
    completed = []
    in_done_section = False
    for line in lines:
        if line.strip() == "## Già fatto":
            in_done_section = True
            open_lines.append(line)
            continue

        if in_done_section:
            if line.startswith("## ") and not line.startswith("## Già fatto"):
                in_done_section = False
                open_lines.append(line)
            else:
                if line.strip() and not line.strip().startswith("_("):
                    completed.append(line)
                else:
                    open_lines.append(line)
        else:
            if line.startswith("- [x]") or line.startswith("- [X]"):
                completed.append(line)
                # also grab subsequent indented lines if any? We assume single line for now for simplicity
            else:
                open_lines.append(line)

    if not completed:
        print("Nessun elemento da flushare in CHANGELOG.md.")
        return

    # Flush completed to CHANGELOG.md under [Unreleased]
    if os.path.exists(CHANGELOG_FILE):
        with open(CHANGELOG_FILE, "r", encoding="utf-8") as f:
            cl = f.read()

        # Insert under ## [Unreleased]
        if "## [Unreleased]" in cl:
            parts = cl.split("## [Unreleased]")
            new_cl = parts[0] + "## [Unreleased]\n"
            for c in completed:
                # Strip checkboxes
                clean = re.sub(r"^- \[[xX]\] ", "- ", c.strip())
                new_cl += f"{clean}\n"
            new_cl += parts[1]

            with open(CHANGELOG_FILE, "w", encoding="utf-8") as f:
                f.write(new_cl)

            # Now rewrite ToDo.md empty Già fatto
            with open(TODO_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(open_lines))
            print(f"Flushate {len(completed)} voci in CHANGELOG.md.")
        else:
            print("CHANGELOG.md non contiene '## [Unreleased]'.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "flush":
        flush_todo()
    else:
        print("Usage: python3 agent-todo.py flush")

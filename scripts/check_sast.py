#!/usr/bin/env python3
import os
import re
import sys

SAST_RULES = [
    (r"\bexec\s*\(", "Use of dynamic exec()"),
    (r"\beval\s*\(", "Use of dynamic eval()"),
    (r"\bos\.system\s*\(", "Use of os.system() (prefer subprocess with safe args)"),
    (r"\bpickle\.load", "Insecure deserialization with pickle"),
    (r"\byaml\.load\s*\([^)]*\)", "Insecure yaml.load (use yaml.safe_load)"),
]

def scan_file(filepath: str) -> list[tuple[int, str]]:
    if os.path.basename(filepath).startswith("test_") or filepath.endswith("check_sast.py"):
        return []
    findings = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            for line_no, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                for pattern, desc in SAST_RULES:
                    if re.search(pattern, line):
                        findings.append((line_no, desc))
    except OSError:
        pass
    return findings

def main() -> int:
    violations = 0
    gateway_files = ["gateway_core.py", "global_config.py", "laya_service.py", "router.py"]
    for filename in gateway_files:
        if os.path.exists(filename):
            findings = scan_file(filename)
            if findings:
                for line_no, desc in findings:
                    print(f"SAST VIOLATION in {filename}:{line_no} — {desc}")
                    violations += 1

    if violations > 0:
        print(f"SAST audit failed: {violations} code defect(s) detected.")
        return 1
    print("SAST audit passed: gateway code baseline is clean.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

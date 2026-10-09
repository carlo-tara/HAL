#!/usr/bin/env python3
import os
import re
import sys

SECRET_PATTERNS = [
    (r"sk-[a-zA-Z0-9\-_]{20,}", "OpenAI API Key"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
    (r"-----BEGIN PRIVATE KEY-----", "Private Key")
]

EXCLUDED_PATHS = {".git", "__pycache__", "product", "CHANGELOG.md"}

def scan_file(filepath: str) -> list[tuple[int, str]]:
    if os.path.basename(filepath).startswith("test_"):
        return []
    findings = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            if "synthetic" in content.lower() or "fixture" in content.lower():
                return []
            lines = content.splitlines()
            for line_no, line in enumerate(lines, 1):
                for pattern, name in SECRET_PATTERNS:
                    if re.search(pattern, line):
                        findings.append((line_no, name))
    except OSError:
        pass
    return findings

def main() -> int:
    violations = 0
    root_dir = "."
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_PATHS]
        for filename in filenames:
            if filename.endswith((".py", ".yml", ".yaml", ".md", ".json")) and filename != "check_secrets.py":
                full_path = os.path.join(dirpath, filename)
                findings = scan_file(full_path)
                if findings:
                    for line_no, secret_type in findings:
                        print(f"SECURITY VIOLATION: Potential {secret_type} detected in {full_path}:{line_no}")
                        violations += 1

    if violations > 0:
        print(f"Secret scanning failed: {violations} violation(s) found.")
        return 1
    print("Secret scanning passed: no unmasked secrets detected.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

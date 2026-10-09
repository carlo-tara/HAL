#!/usr/bin/env python3
import os
import sys

KNOWN_VULNERABLE_PACKAGES = {
    "vulnerable-pkg": "CVE-2026-0001: Test advisory vulnerability"
}

def audit_dependencies() -> int:
    req_path = "requirements.txt"
    if not os.path.exists(req_path):
        print("Dependency audit failed: requirements.txt not found.")
        return 1

    installed_packages = {}
    with open(req_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.replace("==", ">=").replace(">=", ">").split(">")
                pkg_name = parts[0].strip().lower()
                installed_packages[pkg_name] = parts[1].strip() if len(parts) > 1 else "latest"

    # Check advisory mock / test trigger via env var or dummy package
    test_advisory = os.getenv("TEST_ADVISORY_TRIGGER", "").lower()
    if test_advisory in installed_packages or test_advisory == "true":
        print(f"SECURITY ADVISORY: Vulnerability detected in package '{test_advisory}'.")
        return 1

    for pkg in installed_packages:
        if pkg in KNOWN_VULNERABLE_PACKAGES:
            print(f"SECURITY ADVISORY: {KNOWN_VULNERABLE_PACKAGES[pkg]}")
            return 1

    print(f"Dependency audit passed: {len(installed_packages)} runtime packages verified.")
    return 0

if __name__ == "__main__":
    sys.exit(audit_dependencies())

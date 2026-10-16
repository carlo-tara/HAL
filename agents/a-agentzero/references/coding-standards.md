# Coding Standards — HAL Agent L0

## Python Conventions

### Datetime
- Prefer `datetime.UTC` over `datetime.timezone.utc` (available in Python 3.11+).

### Linter Tags (Ruff/Pyright/Diagnostics)
- **Silent Failures**: When a `try-except-pass` block is intentional (e.g., for optional dependencies like `torch` or `cuda` cleanup), use:
  ```python
  try:
      # ...
  except Exception:  # noqa: BLE001, S110
      pass
  ```
  - `BLE001`: Do not catch blind exception `Exception`.
  - `S110`: `try`-`except`-`pass` detected.

## API Consistency
- Internal methods (e.g., `_predict_payload`) should provide defaults for optional parameters even if passed as `None` from higher layers.

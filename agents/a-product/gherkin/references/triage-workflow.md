# Triage workflow (`/triage`)

1. Esistono `features/*.feature`?
2. README coverage aggiornato? Inventory UI/IO presente?
3. Route:
   - suite assente → `/create`
   - gap seeds/UI/IO → `/cover` o `/build`
   - solo edge → `/expand`
   - NL nuovo → `/add-scenario`
   - trust/privacy → `/secure`
   - reattività percepita → `/perf`
   - drift post-UI → `/refine`
   - ok → `/validate` o none

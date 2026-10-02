# Lint rules

- Keyword IT coerenti con `# language: it`
- Nessun selettore CSS/XPath/coordinate nei passi
- Tag noti (vedi tagging.md); niente emoji nei tag
- Scenario senza Then → fail
- Feature senza Scenario → fail
- Duplicati di titolo Scenario nello stesso file → fail
- Given che cita "come nello scenario precedente" → fail (order dependence)

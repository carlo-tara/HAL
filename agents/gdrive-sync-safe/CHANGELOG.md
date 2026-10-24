# Changelog — gdrive-sync-safe

## [1.0.1] - 2026-10-24

### Added

- Regola 4: pausare `gdrive-export-watchdog.service` durante l editing dei repo in `/var/www` (ripristina i file allo snapshot di Drive; le modifiche locali possono sparire senza errore).

---
name: gdrive-sync-safe
version: 1.0.1
description: Guide to safely manage local Google Drive mirrors and prevent IDE freezes or recursive index locking.
---

# Google Drive Safe Local Sync & IDE Management

Use this skill when dealing with large local mirror directories of Google Drive (`/var/www/gDrive`) to prevent IDE performance drops, high CPU load, or crashes.

## Key Rules
1. **Never Index GDrive in Code Workspaces**: Keep `/var/www/gDrive` excluded from Zed/Cursor workspace file search, file watching, and folder navigation unless specifically querying targeted individual files.
2. **Exclude in IDE Settings**: Ensure `.vscode/settings.json` or project settings contain:
   ```json
   {
     "files.exclude": { "**/gDrive": true },
     "search.exclude": { "**/gDrive": true },
     "files.watcherExclude": { "**/gDrive/**": true }
   }
   ```
3. **Targeted Operations**: When running sync scripts or operations inside large mirror directories, use targeted relative paths instead of wildcard recursive actions across the whole repository.
4. **Pause the export watchdog while editing**: the user service `gdrive-export-watchdog.service` (`~/gdrive-ops/scripts/export_watchdog.py`, ~45s interval) rewrites files under `/var/www` repos, restoring them to the Drive snapshot; local edits (even via `edit_file`/`write_file`) can vanish with no error. Before editing a synced repo run `systemctl --user stop gdrive-export-watchdog.service`, and restart it at the end of the session with `systemctl --user start gdrive-export-watchdog.service`. Typical symptom: `write_file`/`edit_file` report success but the file is unchanged (frozen mtime) and new untracked files disappear.


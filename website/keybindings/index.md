# Keybindings

LogTUI is designed to be fully controllable through fast, intuitive keyboard shortcuts without requiring a mouse.

## Navigation

| Key | Action | Description |
| --- | --- | --- |
| <kbd>↑</kbd> / <kbd>↓</kbd> | Move cursor | Step up or down line by line |
| <kbd>j</kbd> / <kbd>k</kbd> | Vim navigation | Move down (<kbd>j</kbd>) or up (<kbd>k</kbd>) |
| <kbd>g</kbd> | Jump to start | Scroll to the very first log entry |
| <kbd>G</kbd> | Jump to end | Scroll to the latest log entry and enable follow |
| <kbd>Enter</kbd> | Inspect entry | Open the full detail modal with formatted JSON fields |

## Filtering & Search

| Key | Action | Description |
| --- | --- | --- |
| <kbd>/</kbd> | Search / Query | Open the query bar for text or structured queries (e.g. `level:error service:api status:>=500`) |
| <kbd>Escape</kbd> | Clear search | Clear the active search filter and hide the search input |
| <kbd>l</kbd> | Cycle level | Cycle minimum level filter (`ALL` → `DEBUG+` → `INFO+` → `WARN+` → `ERROR+`) |
| <kbd>0</kbd> .. <kbd>4</kbd> | Jump to level | Direct level shortcuts (`0: ALL`, `1: DEBUG+`, `2: INFO+`, `3: WARN+`, `4: ERROR+`) |
| <kbd>s</kbd> | Filter source | Cycle between source files, or click any source in the sidebar |
| <kbd>e</kbd> | Export logs | Open the export modal to save filtered entries to `.jsonl`, `.json`, or `.csv` |

## Streaming & Control

| Key | Action | Description |
| --- | --- | --- |
| <kbd>Space</kbd> | Pause / Resume | Toggle pause. Incoming entries continue to be buffered in the background |
| <kbd>f</kbd> | Auto-follow | Toggle auto-follow mode (automatically scrolls down on new incoming logs) |
| <kbd>?</kbd> | Help | Display the keyboard shortcut cheatsheet modal |
| <kbd>q</kbd> | Quit / Dismiss | Close any open modal screen or exit LogTUI |

## Modal Screen Shortcuts

When inside the **Detail** screen (<kbd>Enter</kbd>):
- <kbd>c</kbd> : Copy the raw log content / JSON to system clipboard.
- <kbd>Esc</kbd> / <kbd>q</kbd> : Dismiss dialog and return to the log table.

When inside the **Export** screen (<kbd>e</kbd>):
- <kbd>Enter</kbd> : Confirm export to the chosen filename.
- <kbd>Esc</kbd> / <kbd>q</kbd> : Cancel export.

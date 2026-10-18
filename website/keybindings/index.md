# Keybindings

LogTUI is designed to remain usable without a mouse.

| Key | Action |
| --- | --- |
| <kbd>↑</kbd> / <kbd>↓</kbd> | Move through log entries |
| <kbd>j</kbd> / <kbd>k</kbd> | Move using Vim-style keys |
| <kbd>g</kbd> / <kbd>G</kbd> | Jump to first / last log |
| <kbd>Enter</kbd> | Inspect the selected entry |
| <kbd>Space</kbd> | Pause or resume the visible stream |
| <kbd>f</kbd> | Toggle auto-follow mode |
| <kbd>l</kbd> | Cycle minimum log level (`ALL`, `INFO+`, `WARN+`, `ERROR+`) |
| <kbd>0</kbd>..`4` | Direct jump to level filter |
| <kbd>s</kbd> | Filter by source file (or click sidebar) |
| <kbd>/</kbd> | Search across all log fields |
| <kbd>?</kbd> | Open the integrated help |
| <kbd>q</kbd> | Close a dialog or quit LogTUI |

When paused, incoming entries continue to be collected. Resume the stream to add
them to the table.

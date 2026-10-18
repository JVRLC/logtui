# LogTUI

> A fast terminal UI for exploring and filtering logs.

**[Website](https://jvrlc.github.io/logtui/)** ·
**[Getting started](#install)** ·
**[Contributing](CONTRIBUTING.md)**

LogTUI reads local log files, normalizes JSONL and plain-text entries, and follows
new lines in a navigable terminal table. It is local-only and needs no server.

```bash
logtui app.log
logtui api.log worker.log
```

![LogTUI screenshot placeholder](docs/screenshot-placeholder.svg)

## Install

Python 3.12 or newer is required.

```bash
pip install .
# or
pipx install .
```

For development:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pytest
```

## Usage

```bash
logtui app.log
logtui api.log worker.log --buffer-size 20000
logtui docker:my-api
logtui app.log --level ERROR --export errors.jsonl
logtui app.log --jsonl
docker logs -f my-api | logtui -
```

JSON objects are mapped to timestamp, level, service, and message. Extra fields
remain available in the detail view. Unknown or invalid formats safely become
plain text. Multi-line stacktraces are automatically grouped into their parent error.

### Keyboard shortcuts

| Key | Action |
| --- | --- |
| `↑` / `↓` | Navigate |
| `j` / `k` | Navigate using Vim-style keys |
| `g` / `G` | Jump to first / last log |
| `Enter` | Open log details and JSON |
| `Space` | Pause/resume display |
| `f` | Toggle auto-follow mode |
| `l` / `0..4` | Filter by minimum log level (`ALL`, `INFO+`, `WARN+`, `ERROR+`) |
| `s` | Filter by source file (or click on sidebar) |
| `e` | Export filtered logs to file (`.jsonl`, `.json`, `.csv`) |
| `/` | Search or structured query (e.g. `level:error service:api`) |
| `?` | Open keyboard help |
| `q` | Quit or close details |

## Roadmap

The completed milestones include an independently tested query language, headless JSONL
output, JSON/CSV exports, multi-line stacktrace grouping, and native Docker sources.

The package is separated into sources, parsing, models, buffer, and TUI layers so
future Kubernetes, journald, and custom parser integrations can remain
optional.

## Contributing

Run `pytest`, `ruff check .`, `ruff format --check .`, and `mypy` before opening a
change. Focused bug reports and small, tested pull requests are welcome.

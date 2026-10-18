# Getting Started

Get up and running with LogTUI in seconds.

## Requirements

- Python 3.12 or newer
- Modern terminal with ANSI color support (macOS Terminal, iTerm2, Kitty, Alacritty, WezTerm, Ghostty, Windows Terminal)

## Installation

### With pipx (recommended)

```bash
pipx install git+https://github.com/JVRLC/logtui.git
```

### With uv

```bash
uv tool install git+https://github.com/JVRLC/logtui.git
```

### For local development

```bash
git clone https://github.com/JVRLC/logtui.git
cd logtui
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

---

## Basic Usage

### 1. Open a local log file

```bash
logtui app.log
```

LogTUI loads existing lines and automatically tails newly appended entries in real time.

### 2. Multi-source streaming

```bash
logtui api.log worker.log nginx.log
```

Each source is color-coded and listed in the sidebar with live counters.

### 3. Docker container logs

```bash
logtui docker:my-api-server
```

---

## Filtering on Launch

Start LogTUI with pre-applied filters so you see only what matters:

```bash
# Filter by log level
logtui demo.log --level ERROR

# Filter by structured query
logtui demo.log --query "level:ERROR status:>=500"

# Initial free-text search
logtui demo.log --search "timeout"
```

---

## Headless CLI & Export Mode

Use LogTUI non-interactively in shell scripts or CI/CD pipelines:

```bash
# Export matching errors to JSON Lines
logtui demo.log --headless --query "level:ERROR" --export errors.jsonl

# Export to CSV
logtui demo.log --headless --query "service:billing" --export billing.csv

# Print JSON Lines directly to stdout
logtui demo.log --headless --jsonl | jq .
```

---

## Try the Included Demo

Test all features right away with the included sample log or live simulator:

```bash
# Explore demo log
logtui demo.log

# Or run the live streaming simulator
python generate_logs.py demo.log
```

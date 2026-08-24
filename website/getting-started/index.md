# Getting started

## Requirements

- Python 3.12 or newer
- A terminal with modern color support

## Install

Install the current version directly from GitHub:

```bash
pipx install git+https://github.com/JVRLC/logtui.git
```

For local development:

```bash
git clone https://github.com/JVRLC/logtui.git
cd logtui
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

## Open a log file

```bash
logtui app.log
```

LogTUI reads the current file and keeps following newly appended lines.

## Open several files

```bash
logtui api.log worker.log nginx.log
```

Each entry keeps its original source. Use `--buffer-size` to change the maximum
number of entries retained in memory:

```bash
logtui app.log --buffer-size 20000
```

## Try the included demo

From a development checkout:

```bash
logtui demo.log
```

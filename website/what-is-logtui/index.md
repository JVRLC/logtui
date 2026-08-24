# What is LogTUI?

LogTUI is a fast terminal interface for reading, following and inspecting logs.
It is designed for developers who want immediate answers from local files without
setting up a log platform.

## A TUI for everyday debugging

LogTUI reads all existing lines, follows new entries like `tail -f`, and keeps a
bounded history in memory. The interface shows the timestamp, level, service,
source and message while preserving structured fields for detailed inspection.

```bash
logtui app.log
```

## Local first

The core does not require Elasticsearch, Kafka, ClickHouse, Grafana or a remote
server. Your logs stay on your machine and the application starts immediately.

## Format tolerant

JSONL and standard Python logs are recognized automatically. Unknown or malformed
entries safely fall back to plain text, so an unexpected line cannot stop the
stream.

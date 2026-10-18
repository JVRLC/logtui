# What is LogTUI?

**LogTUI** is a fast, keyboard-first terminal user interface designed to read, follow, filter, and inspect logs in real time. It is built for developers, DevOps, and SREs who want immediate visibility into local distributed systems and Docker containers without the overhead of heavy observability platforms.

---

## The Terminal-Native Log Experience

Traditional commands like `tail -f` and `grep` are ubiquitous, but they struggle with modern multi-service applications: JSON blobs become unreadable walls of text, stacktraces split into hundreds of disconnected lines, and filtering on structured fields (e.g. `status >= 500`) requires complex `jq` pipelines.

LogTUI solves this by providing a unified terminal dashboard:

- **Unified Multi-Stream Timeline** : Merge multiple local log files and running Docker containers (`docker:<name>`) into a single synchronized view.
- **Structured By Default** : Automatic schema extraction maps timestamps, severity levels, service names, and custom attributes.
- **Zero Overhead** : Starts in less than 50 milliseconds. Bounded memory ring buffer ensures your terminal stays responsive even during heavy bursts.

```bash
logtui api.log worker.log docker:redis-service
```

---

## Key Pillars

### 1. 100% Local-First
No Elasticsearch cluster, no Grafana Loki agent, no ClickHouse, and no external cloud credentials. Your logs never leave your workstation, and you can diagnose incidents entirely offline.

### 2. Intelligent Format & Exception Handling
- **JSON Lines** : Nested keys and metadata are parsed and preserved.
- **Python, Java, Go & Node Stacktraces** : Multi-line error tracebacks are folded into single logical events with automatic `ERROR` severity elevation.
- **Plain Text Fallback** : Unstructured text is safely preserved.

### 3. In-Memory Query Language
Filter live and historical logs with high-performance predicate evaluation:
```bash
/level:ERROR status:>=500 -service:auth "connection timeout"
```

### 4. Interactive & Headless Modes
Inspect complex JSON payloads with syntax highlighting (<kbd>Enter</kbd>), copy raw events to the clipboard (<kbd>c</kbd>), or run headless in shell scripts to export filtered logs to `.jsonl` or `.csv`.

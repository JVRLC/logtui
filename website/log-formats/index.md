# Log formats & Querying

LogTUI automatically normalizes heterogeneous log formats into a unified schema with timestamps, levels, service names, source tags, messages, and arbitrary structured fields.

## Supported Formats

### 1. JSON Lines (JSONL)

JSON logs are parsed automatically without any configuration. Standard keys (`timestamp`, `time`, `level`, `lvl`, `severity`, `service`, `app`, `message`, `msg`) are mapped directly to table columns, while all extra keys (e.g. `request_id`, `status`, `duration_ms`) are indexed as structured fields:

```json
{
  "timestamp": "2026-10-18T10:06:35Z",
  "level": "ERROR",
  "service": "database",
  "message": "Database query timeout",
  "request_id": "req_a1b322",
  "status": 504,
  "duration_ms": 3004
}
```

### 2. Standard Text & Python Logs

Standard application logs containing timestamps and log levels are parsed cleanly:

```text
2026-10-18 10:14:35 - ERROR - [worker] Unable to rotate archived log file
```

### 3. Multi-Line & Stacktrace Aggregation

LogTUI automatically identifies continuation lines and stacktraces from Python (`Traceback (most recent call last):`), Java (`at com.example...`), Go, and NodeJS.

Instead of polluting your stream with dozens of broken lines, the entire exception is aggregated into the originating event, and the log severity is automatically elevated to `ERROR`.

```text
2026-10-18 10:15:00 - ERROR - Exception during request processing
Traceback (most recent call last):
  File "app/server.py", line 42, in handle_request
    result = db.query("SELECT * FROM users")
ConnectionError: Connection refused to postgres:5432
```

### 4. Plain Text Fallback

Unstructured text lines are never dropped. They are preserved with their exact content and source tag.

---

## Structured Query Engine

LogTUI features an embedded query language accessible via `/` in the TUI or `--query` in the CLI.

### Query Syntax

| Query Syntax | Description | Example |
| --- | --- | --- |
| `level:<LEVEL>` | Match level exactly or with minimum weight (`+`) | `level:ERROR` or `level:WARN+` |
| `service:<NAME>` | Filter by service name | `service:auth` |
| `source:<NAME>` | Filter by source file or container | `source:api.log` or `source:docker:backend` |
| `<field>:<value>` | Match exact or substring field value | `method:POST` |
| `<field>:>=<num>` | Numeric comparison (`>=`, `<=`, `>`, `<`) | `status:>=500` or `duration_ms:>1000` |
| `-<field>:<val>` | Negation (exclude matches) | `-service:auth` or `-status:200` |
| `"quoted text"` | Exact phrase search | `"connection reset by peer"` |
| `word1 word2` | Free-text search across all fields (AND logic) | `database timeout` |

### Query Examples

```bash
# Filter errors from the billing service with duration >= 1 second
logtui demo.log --query "level:ERROR service:billing duration_ms:>=1000"

# Show all 5xx server errors, excluding auth service
logtui demo.log --query "status:>=500 -service:auth"
```

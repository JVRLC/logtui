# Log formats

Every parser produces the same normalized log entry with a timestamp, level,
service, message, source and additional fields.

## JSON Lines

Known keys are mapped automatically. All other values remain available in the
detail view.

```json
{
  "timestamp": "2026-08-24T09:06:35Z",
  "level": "ERROR",
  "service": "database",
  "message": "Database query timeout",
  "request_id": "req_a1b322",
  "duration_ms": 3004
}
```

## Python logs

Standard lines containing an ISO-like timestamp and a known log level are split
into structured values.

```text
2026-08-24 09:14:35 - ERROR - Unable to rotate archived log file
```

## Plain text fallback

Anything that cannot be parsed remains visible as plain text. LogTUI never drops
an entry merely because its format is unknown.

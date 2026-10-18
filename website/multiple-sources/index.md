# Multiple Sources & Streaming

LogTUI can consume and merge multiple concurrent log streams into a single unified timeline.

## Multi-File Streaming

Pass several file paths to tail them simultaneously:

```bash
logtui api.log worker.log nginx.log
```

Each source runs as an independent async streaming task. A slow or idle file never blocks active sources.

## Docker Containers

Stream logs directly from running Docker containers using the `docker:<container_name>` prefix:

```bash
logtui docker:my-api-container
```

You can even mix local log files and Docker containers in the same session:

```bash
logtui api.log docker:redis-service docker:postgres
```

## Waiting for File Creation

If a log file does not exist yet (e.g. during application startup or deployment):

```bash
logtui /var/log/app.log --wait
```

LogTUI will wait patiently until the file is created on disk, then immediately begin tailing new lines.

## Standard Input (Pipes)

Pipe the output of any CLI tool directly into LogTUI using `-`:

```bash
kubectl logs -f deployment/api | logtui -
docker compose logs -f | logtui -
journalctl -u my-service -f | logtui -
```

## Buffer Management

Control the in-memory ring buffer size with `--buffer-size` (default: 10,000 entries):

```bash
logtui api.log --buffer-size 50000
```

When the buffer reaches capacity, the oldest entries are discarded automatically without blocking your system or consuming excessive memory. The sidebar constantly displays your active buffer usage.

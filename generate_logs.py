#!/usr/bin/env python3
"""Simulate a live stream of log entries for testing LogTUI."""

import datetime
import json
import random
import sys
import time

SERVICES = ["api", "auth", "database", "worker", "billing", "cache"]
LEVELS = ["DEBUG", "INFO", "INFO", "INFO", "WARN", "ERROR"]

MESSAGES = {
    "api": [
        ("GET /api/v1/users", 200),
        ("POST /api/v1/orders", 201),
        ("GET /api/v1/items", 200),
        ("DELETE /api/v1/session", 204),
        ("PUT /api/v1/settings", 500),
    ],
    "auth": [
        "Token verified successfully",
        "User logged in from new IP",
        "Invalid password attempt",
        "Session expired",
    ],
    "database": [
        "Connection pool size: 10/20",
        "Query executed in 14ms",
        "Slow query detected: SELECT * FROM audit_logs (1820ms)",
        "Deadlock detected on table reservations",
    ],
    "worker": [
        "Processed background email job",
        "Image thumbnail generated",
        "Queue depth: 42 messages pending",
        "Worker retry 2/3 for invoice PDF export",
    ],
    "billing": [
        "Payment intent created",
        "Stripe webhook received",
        "Subscription renewed: plan_pro",
        "Payment failed: card declined",
    ],
    "cache": [
        "Cache hit ratio: 94.2%",
        "Evicted 12 keys under memory pressure",
        "Redis ping latency: 1.2ms",
    ],
}


def generate_entry() -> str:
    service = random.choice(SERVICES)
    level = random.choice(LEVELS)
    now = datetime.datetime.now(datetime.UTC).isoformat()

    msg_data = random.choice(MESSAGES[service])
    if isinstance(msg_data, tuple):
        message, status = msg_data
        entry = {
            "timestamp": now,
            "level": "ERROR" if status >= 500 else level,
            "service": service,
            "message": message,
            "status": status,
            "duration_ms": random.randint(5, 1200),
        }
    else:
        entry = {
            "timestamp": now,
            "level": level,
            "service": service,
            "message": msg_data,
            "latency_ms": random.randint(1, 150),
        }
    return json.dumps(entry)


def main() -> None:
    target_file = sys.argv[1] if len(sys.argv) > 1 else "demo.log"
    interval = float(sys.argv[2]) if len(sys.argv) > 2 else 0.4

    print(f"Streaming random logs into '{target_file}' every {interval}s (Ctrl+C to stop)...")
    with open(target_file, "a", encoding="utf-8") as f:
        while True:
            line = generate_entry()
            f.write(line + "\n")
            f.flush()
            print(f">> {line}")
            time.sleep(interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStream stopped.")

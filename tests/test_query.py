from logtui.models import LogEntry
from logtui.parsing.query import Query


def test_query_freetext_search() -> None:
    query = Query("database timeout")
    e1 = LogEntry(message="database connection timeout", source="api.log")
    e2 = LogEntry(message="server started successfully", source="api.log")

    assert query.matches(e1)
    assert not query.matches(e2)


def test_query_level_and_service() -> None:
    query = Query("level:ERROR service:api")
    e1 = LogEntry(level="ERROR", service="api", message="boom", source="app.log")
    e2 = LogEntry(level="WARN", service="api", message="boom", source="app.log")
    e3 = LogEntry(level="ERROR", service="worker", message="boom", source="app.log")

    assert query.matches(e1)
    assert not query.matches(e2)
    assert not query.matches(e3)


def test_query_level_plus_and_comparison() -> None:
    query = Query("level:WARN+")
    e_debug = LogEntry(level="DEBUG", message="m", source="s")
    e_info = LogEntry(level="INFO", message="m", source="s")
    e_warn = LogEntry(level="WARN", message="m", source="s")
    e_err = LogEntry(level="ERROR", message="m", source="s")

    assert not query.matches(e_debug)
    assert not query.matches(e_info)
    assert query.matches(e_warn)
    assert query.matches(e_err)


def test_query_custom_fields_numeric_and_text() -> None:
    q_num = Query("status:>=400 duration_ms:>100")
    e1 = LogEntry(
        message="req",
        source="s",
        fields={"status": 500, "duration_ms": 250},
    )
    e2 = LogEntry(
        message="req",
        source="s",
        fields={"status": 200, "duration_ms": 300},
    )
    e3 = LogEntry(
        message="req",
        source="s",
        fields={"status": 404, "duration_ms": 50},
    )

    assert q_num.matches(e1)
    assert not q_num.matches(e2)
    assert not q_num.matches(e3)


def test_query_negation() -> None:
    query = Query("level:ERROR -service:auth")
    e1 = LogEntry(level="ERROR", service="api", message="fail", source="s")
    e2 = LogEntry(level="ERROR", service="auth", message="fail", source="s")

    assert query.matches(e1)
    assert not query.matches(e2)


def test_query_source_and_quoted_phrase() -> None:
    query = Query('source:worker.log "connection reset"')
    e1 = LogEntry(message="Error: connection reset by peer", source="worker.log")
    e2 = LogEntry(message="Error: connection reset by peer", source="api.log")

    assert query.matches(e1)
    assert not query.matches(e2)


def test_query_operators() -> None:
    q_lt = Query("duration_ms:<=50 level:!=DEBUG msg:error")
    e1 = LogEntry(
        level="INFO",
        message="an error occurred",
        source="s",
        fields={"duration_ms": 30},
    )
    e2 = LogEntry(
        level="DEBUG",
        message="an error occurred",
        source="s",
        fields={"duration_ms": 30},
    )
    e3 = LogEntry(
        level="INFO",
        message="an error occurred",
        source="s",
        fields={"duration_ms": 100},
    )

    assert q_lt(e1)
    assert not q_lt(e2)
    assert not q_lt(e3)

    q_less = Query("duration_ms:<50")
    assert q_less.matches(e1)
    assert not q_less.matches(e3)

    # Invalid float conversion fallback
    e_str = LogEntry(message="bad", source="s", fields={"duration_ms": "not_a_number"})
    assert not q_less.matches(e_str)

    # Empty query matches everything
    q_empty = Query("")
    assert q_empty.matches(e1)


def test_query_freetext_field_matches() -> None:
    e = LogEntry(
        message="simple msg",
        level="WARN",
        service="checkout-service",
        source="server-3.log",
        fields={"customer_id": "cust_12345"},
        raw="raw log content",
    )
    assert Query("checkout-service").matches(e)
    assert Query("server-3").matches(e)
    assert Query("cust_12345").matches(e)
    assert Query("raw log").matches(e)
    assert Query("customer_id").matches(e)
    assert not Query("nonexistent").matches(e)

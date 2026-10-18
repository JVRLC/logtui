import re
from collections.abc import Callable

from logtui.models import LogEntry

LEVEL_WEIGHTS: dict[str, int] = {
    "TRACE": 5,
    "DEBUG": 10,
    "INFO": 20,
    "WARN": 30,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50,
    "FATAL": 50,
}

TERM_PATTERN = re.compile(
    r"(?P<neg>-|!)?"
    r"(?:(?P<key>[a-zA-Z_][a-zA-Z0-9_\.]*):(?P<op>>=|<=|>|<|!=|=)?)?"
    r'(?:"(?P<quoted>[^"]*)"|(?P<word>\S+))'
)


class Query:
    """Compiled query for filtering log entries."""

    def __init__(self, raw: str) -> None:
        self.raw = raw.strip()
        self._predicates: list[Callable[[LogEntry], bool]] = []
        self._compile()

    def _compile(self) -> None:
        if not self.raw:
            return

        for match in TERM_PATTERN.finditer(self.raw):
            negated = bool(match.group("neg"))
            key = match.group("key")
            op = match.group("op") or "="
            value = (
                match.group("quoted") if match.group("quoted") is not None else match.group("word")
            )
            if value is None:
                continue

            pred = self._build_predicate(key, op, value)
            if negated:
                pred = self._negate(pred)
            self._predicates.append(pred)

    @staticmethod
    def _negate(pred: Callable[[LogEntry], bool]) -> Callable[[LogEntry], bool]:
        return lambda entry: not pred(entry)

    def _build_predicate(self, key: str | None, op: str, value: str) -> Callable[[LogEntry], bool]:
        val_lower = value.casefold()

        # General free-text search across all fields
        if not key:
            return lambda entry: self._match_freetext(entry, val_lower)

        key_lower = key.casefold()

        if key_lower == "level":
            return self._build_level_predicate(op, value)

        if key_lower == "service":
            return lambda entry: entry.service is not None and val_lower in entry.service.casefold()

        if key_lower in ("source", "src", "file"):
            return lambda entry: entry.source is not None and val_lower in entry.source.casefold()

        if key_lower in ("message", "msg"):
            return lambda entry: val_lower in entry.message.casefold()

        # Field search in entry.fields
        return lambda entry: self._match_custom_field(entry, key, op, value)

    def _build_level_predicate(self, op: str, value: str) -> Callable[[LogEntry], bool]:
        clean_val = value.rstrip("+").upper()
        target_weight = LEVEL_WEIGHTS.get(clean_val, 0)
        is_plus = value.endswith("+") or op in (">=", ">")

        def check_level(entry: LogEntry) -> bool:
            if not entry.level:
                return False
            lvl_weight = LEVEL_WEIGHTS.get(entry.level.upper(), 0)
            if is_plus:
                return lvl_weight >= target_weight
            if op == "!=":
                return lvl_weight != target_weight
            return lvl_weight == target_weight

        return check_level

    @staticmethod
    def _match_custom_field(entry: LogEntry, key: str, op: str, value: str) -> bool:
        if not entry.fields or key not in entry.fields:
            return False
        field_val = entry.fields[key]

        # Numeric comparison if applicable
        if op in (">=", "<=", ">", "<"):
            try:
                num_field = float(field_val)
                num_target = float(value)
                if op == ">=":
                    return num_field >= num_target
                if op == "<=":
                    return num_field <= num_target
                if op == ">":
                    return num_field > num_target
                if op == "<":
                    return num_field < num_target
            except (ValueError, TypeError):
                return False

        field_str = str(field_val).casefold()
        val_str = value.casefold()
        if op == "!=":
            return field_str != val_str
        return val_str in field_str

    @staticmethod
    def _match_freetext(entry: LogEntry, query: str) -> bool:
        if entry.raw and query in entry.raw.casefold():
            return True
        if query in entry.message.casefold():
            return True
        if entry.level and query in entry.level.casefold():
            return True
        if entry.service and query in entry.service.casefold():
            return True
        if entry.source and query in entry.source.casefold():
            return True
        if entry.fields:
            for k, v in entry.fields.items():
                if query in str(k).casefold() or query in str(v).casefold():
                    return True
        return False

    def matches(self, entry: LogEntry) -> bool:
        """Check if log entry matches all predicates (AND logic)."""
        if not self._predicates:
            return True
        return all(predicate(entry) for predicate in self._predicates)

    def __call__(self, entry: LogEntry) -> bool:
        return self.matches(entry)

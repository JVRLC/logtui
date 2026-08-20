from logtui.models import LogEntry
from logtui.parsing.json_parser import JsonParser
from logtui.parsing.text_parser import TextParser


class AutoDetectParser:
    """Try structured parsing and always fall back to lossless plain text."""

    def __init__(self) -> None:
        self._json = JsonParser()
        self._text = TextParser()

    def parse(self, line: str, source: str) -> LogEntry:
        if line.lstrip().startswith(("{", "[")):
            try:
                return self._json.parse(line, source)
            except (ValueError, TypeError):
                pass
        return self._text.parse(line, source)

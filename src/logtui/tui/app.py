import asyncio
import json
from collections import Counter
from collections.abc import Sequence
from functools import partial
from pathlib import Path
from typing import Any

from rich.syntax import Syntax
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Header, Input, Label, Static

from logtui.buffer import RingBuffer
from logtui.models import LogEntry
from logtui.parsing import AutoDetectParser
from logtui.sources.base import LogSource

LEVEL_STYLES = {
    "DEBUG": "dim cyan",
    "INFO": "bold green",
    "WARN": "bold yellow",
    "WARNING": "bold yellow",
    "ERROR": "bold red",
    "CRITICAL": "bold white on red",
}


class DetailScreen(ModalScreen[None]):
    BINDINGS = [Binding("escape", "dismiss", "Back"), Binding("q", "dismiss", "Back")]
    CSS = """
    DetailScreen { align: center middle; background: $background 70%; }
    #detail-dialog {
        width: 82%; height: 84%; max-width: 110;
        padding: 1 2; border: tall $accent; background: $surface;
    }
    #detail-title { height: 2; text-style: bold; color: $accent; }
    #detail-summary { height: auto; margin-bottom: 1; color: $text-muted; }
    #detail-message {
        height: auto; max-height: 8; padding: 1;
        border-left: thick $accent; background: $panel;
    }
    #detail-fields-title { height: 2; margin-top: 1; text-style: bold; }
    #detail-fields { height: 1fr; overflow: auto; }
    #detail-hint { height: 1; color: $text-muted; text-align: right; }
    """

    def __init__(self, entry: LogEntry) -> None:
        super().__init__()
        self.entry = entry

    def compose(self) -> ComposeResult:
        timestamp = self.entry.timestamp.isoformat() if self.entry.timestamp else "—"
        summary = (
            f"[b]Time[/b]  {timestamp}    [b]Level[/b]  {self.entry.level or '—'}\n"
            f"[b]Service[/b]  {self.entry.service or '—'}    "
            f"[b]Source[/b]  {self.entry.source}"
        )
        fields = self.entry.fields or {"raw": self.entry.raw or self.entry.message}
        with Vertical(id="detail-dialog"):
            yield Label("Log entry details", id="detail-title")
            yield Label(summary, id="detail-summary")
            yield Static(self.entry.message, id="detail-message")
            yield Label("Structured fields", id="detail-fields-title")
            yield Static(
                Syntax(json.dumps(fields, indent=2, default=str), "json", word_wrap=True),
                id="detail-fields",
            )
            yield Label("esc / q  close", id="detail-hint")

    async def action_dismiss(self, result: None = None) -> None:
        self.dismiss(result)


class HelpScreen(ModalScreen[None]):
    BINDINGS = [
        Binding("escape", "dismiss", "Back"),
        Binding("q", "dismiss", "Back"),
        Binding("?", "dismiss", "Back"),
    ]
    CSS = """
    HelpScreen { align: center middle; background: $background 70%; }
    #help-dialog {
        width: 58; height: auto; padding: 1 2;
        border: tall $accent; background: $surface;
    }
    #help-title { height: 2; text-style: bold; color: $accent; }
    #help-keys { height: auto; }
    #help-hint { height: 2; padding-top: 1; color: $text-muted; text-align: right; }
    """

    def compose(self) -> ComposeResult:
        keys = (
            "[b]↑ / ↓  j / k[/b]    Navigate logs\n"
            "[b]enter[/b]            Inspect selected log\n"
            "[b]space[/b]            Pause or resume the stream\n"
            "[b]/[/b]                Search all log fields\n"
            "[b]?[/b]                Toggle this help\n"
            "[b]q[/b]                Quit LogTUI"
        )
        with Vertical(id="help-dialog"):
            yield Label("Keyboard shortcuts", id="help-title")
            yield Label(keys, id="help-keys")
            yield Label("esc / ? / q  close", id="help-hint")

    async def action_dismiss(self, result: None = None) -> None:
        self.dismiss(result)


class LogTuiApp(App[None]):
    TITLE = "LogTUI"
    SUB_TITLE = "Live log explorer"
    CSS = """
    Screen { background: $background; }
    #workspace { height: 1fr; }
    #sidebar {
        width: 26; min-width: 20; height: 1fr;
        border-right: solid $panel-lighten-2; background: $surface;
    }
    #sources-title {
        height: 1; padding: 0 1;
        color: $text-muted; text-style: bold;
    }
    #sources { height: auto; padding: 0 1; margin-top: 1; }
    .source-row { height: 1; padding: 0 1; color: $text; }
    #sidebar-info {
        height: 2; dock: bottom; padding: 0 1;
        border-top: solid $panel-lighten-2; color: $text-muted;
    }
    #content { width: 1fr; height: 1fr; }
    #table-title {
        height: 1; padding: 0 1;
        text-style: bold; background: $surface;
    }
    #logs { height: 1fr; border: none; }
    #search-input { display: none; height: 3; border: tall $accent; }
    #search-input.visible { display: block; }
    #status-bar {
        height: 1; padding: 0 1;
        background: $panel; color: $text-muted;
    }
    #stream-state { width: 1fr; }
    #stream-count { width: auto; text-align: right; }
    """
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("space", "toggle_pause", "Pause/resume"),
        Binding("enter", "details", "Details"),
        Binding("?", "help", "Help"),
        Binding("/", "search", "Search"),
        Binding("escape", "clear_search", "Clear search", show=False),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

    def __init__(self, sources: Sequence[LogSource], buffer_size: int = 10_000) -> None:
        super().__init__()
        self.sources = list(sources)
        self.entries: RingBuffer[LogEntry] = RingBuffer(buffer_size)
        self.parser = AutoDetectParser()
        self.paused = False
        self._pending_count = 0
        self._source_counts: Counter[str] = Counter()
        self._source_errors: dict[str, str] = {}
        self.search_query = ""
        self._next_id = 0
        self._tasks: list[asyncio.Task[Any]] = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="workspace"):
            with Vertical(id="sidebar"):
                yield Label("SOURCES", id="sources-title")
                with Vertical(id="sources"):
                    for index, source in enumerate(self.sources):
                        marker = "[green]●[/green]" if index == 0 else "[dim]○[/dim]"
                        yield Label(
                            f"{marker}  {self._display_name(source.name)}",
                            classes="source-row",
                            id=f"source-{index}",
                        )
                yield Label(
                    f"Buffer  [b]{self.entries.capacity:,}[/b]\n[dim]entries max[/dim]",
                    id="sidebar-info",
                )
            with Vertical(id="content"):
                yield Label("Live events", id="table-title")
                yield DataTable(cursor_type="row", zebra_stripes=True, id="logs")
                yield Input(placeholder="Search logs…", id="search-input")
                with Horizontal(id="status-bar"):
                    yield Label(
                        "[bold green]● LIVE[/bold green]  Following files", id="stream-state"
                    )
                    yield Label("0 events", id="stream-count")
        yield Footer()

    async def on_mount(self) -> None:
        table = self.query_one("#logs", DataTable)
        table.add_columns("TIME", "LEVEL", "SERVICE", "SOURCE", "MESSAGE")
        table.focus()
        for source in self.sources:
            task = asyncio.create_task(self._consume(source))
            task.add_done_callback(partial(self._source_done, source_name=source.name))
            self._tasks.append(task)

    async def _consume(self, source: LogSource) -> None:
        async for line in source.lines():
            entry = self.parser.parse(line, source.name)
            entry.id = self._next_id
            self._next_id += 1
            self.entries.append(entry)
            self._source_counts[source.name] += 1
            if self.paused:
                self._pending_count += 1
            elif self._matches_search(entry):
                self._add_row(entry)
            self._refresh_chrome()

    def _source_done(self, task: asyncio.Task[Any], source_name: str) -> None:
        if task.cancelled():
            return
        error = task.exception()
        if error is not None:
            self._source_errors[source_name] = str(error)
            self._refresh_chrome()

    def _add_row(self, entry: LogEntry) -> None:
        table = self.query_one("#logs", DataTable)
        timestamp = entry.timestamp.strftime("%H:%M:%S") if entry.timestamp else "—"
        level = entry.level or "—"
        table.add_row(
            Text(timestamp, style="dim"),
            Text(level, style=LEVEL_STYLES.get(level, "dim")),
            entry.service or "—",
            Text(entry.source, style="cyan"),
            entry.message,
            key=str(entry.id),
        )
        overflow = table.row_count - self.entries.capacity
        if overflow > 0:
            for key in list(table.rows)[:overflow]:
                table.remove_row(key)
        if table.row_count:
            table.move_cursor(row=table.row_count - 1)

    def _refresh_chrome(self) -> None:
        pending = f" · {self._pending_count:,} pending" if self._pending_count else ""
        if self._source_errors:
            state = (
                f"[bold red]● SOURCE ERROR[/bold red]  {next(iter(self._source_errors.values()))}"
            )
        elif self.paused:
            state = f"[bold yellow]Ⅱ PAUSED[/bold yellow]{pending}"
        else:
            state = "[bold green]● LIVE[/bold green]  Following files"
        self.query_one("#stream-state", Label).update(state)
        count = len(self.entries)
        if self.search_query:
            visible = self.query_one("#logs", DataTable).row_count
            counter = f"{visible:,} of {count:,} events"
        else:
            counter = f"{count:,} event{'s' if count != 1 else ''}"
        self.query_one("#stream-count", Label).update(counter)
        for index, source in enumerate(self.sources):
            source_name = source.name
            if source_name in self._source_errors:
                marker = "[red]●[/red]"
            else:
                marker = "[green]●[/green]" if self._source_counts[source_name] else "[dim]○[/dim]"
            total = self._source_counts[source_name]
            self.query_one(f"#source-{index}", Label).update(
                f"{marker} {self._display_name(source_name)} [dim]{total:,}[/dim]"
            )

    def _display_name(self, source_name: str) -> str:
        basename = Path(source_name).name
        duplicate_count = sum(Path(source.name).name == basename for source in self.sources)
        return source_name if duplicate_count > 1 else basename

    def action_toggle_pause(self) -> None:
        self.paused = not self.paused
        if not self.paused:
            self._rebuild_table()
            self._pending_count = 0
        self._refresh_chrome()

    def _rebuild_table(self) -> None:
        table = self.query_one("#logs", DataTable)
        table.clear()
        for entry in self.entries:
            if self._matches_search(entry):
                self._add_row(entry)

    def _matches_search(self, entry: LogEntry) -> bool:
        if not self.search_query:
            return True
        haystack = json.dumps(entry.model_dump(mode="json"), default=str).casefold()
        return self.search_query in haystack

    def action_search(self) -> None:
        search = self.query_one("#search-input", Input)
        search.add_class("visible")
        search.value = self.search_query
        search.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "search-input":
            return
        self.search_query = event.value.strip().casefold()
        event.input.remove_class("visible")
        self._rebuild_table()
        self._refresh_chrome()
        self.query_one("#logs", DataTable).focus()

    def action_clear_search(self) -> None:
        search = self.query_one("#search-input", Input)
        if search.has_class("visible"):
            search.remove_class("visible")
            self.query_one("#logs", DataTable).focus()
            return
        if self.search_query:
            self.search_query = ""
            search.value = ""
            self._rebuild_table()
            self._refresh_chrome()

    def action_cursor_down(self) -> None:
        self.query_one("#logs", DataTable).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one("#logs", DataTable).action_cursor_up()

    def action_details(self) -> None:
        table = self.query_one("#logs", DataTable)
        if table.cursor_row < 0 or table.row_count == 0:
            return
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        entry_id = int(str(row_key.value))
        entry = next((item for item in self.entries if item.id == entry_id), None)
        if entry is not None:
            self.push_screen(DetailScreen(entry))

    def action_help(self) -> None:
        self.push_screen(HelpScreen())

    def on_data_table_row_selected(self, _: DataTable.RowSelected) -> None:
        self.action_details()

    async def on_unmount(self) -> None:
        for task in self._tasks:
            task.cancel()

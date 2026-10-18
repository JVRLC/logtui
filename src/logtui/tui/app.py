import asyncio
import json
from collections import Counter
from collections.abc import Sequence
from contextlib import suppress
from functools import partial
from pathlib import Path
from typing import Any, TypeVar

from rich.syntax import Syntax
from rich.text import Text
from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import DataTable, Footer, Header, Input, Label, Static

from logtui.buffer import RingBuffer
from logtui.export import export_logs
from logtui.models import LogEntry
from logtui.parsing import AutoDetectParser
from logtui.parsing.multiline import is_continuation_line, merge_continuation
from logtui.parsing.query import Query
from logtui.sources.base import LogSource

W = TypeVar("W", bound=Widget)

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

LEVEL_FILTERS = ["ALL", "DEBUG+", "INFO+", "WARN+", "ERROR+"]

LEVEL_BADGES: dict[str, tuple[str, str]] = {
    "TRACE": ("TRACE", "dim cyan on #1e293b"),
    "DEBUG": ("DEBUG", "bold #38bdf8 on #0c4a6e"),
    "INFO": ("INFO ", "bold #4ade80 on #052e16"),
    "WARN": ("WARN ", "bold #facc15 on #451a03"),
    "WARNING": ("WARN ", "bold #facc15 on #451a03"),
    "ERROR": ("ERROR", "bold #f87171 on #450a0a"),
    "CRITICAL": ("CRIT ", "bold white on #7f1d1d"),
    "FATAL": ("FATAL", "bold white on #7f1d1d"),
}

LEVEL_STYLES: dict[str, str] = {
    "DEBUG": "dim cyan",
    "INFO": "bold green",
    "WARN": "bold yellow",
    "WARNING": "bold yellow",
    "ERROR": "bold red",
    "CRITICAL": "bold white on red",
}


class DetailScreen(ModalScreen[None]):
    BINDINGS = [
        Binding("escape", "dismiss", "Back"),
        Binding("q", "dismiss", "Back"),
        Binding("c", "copy_raw", "Copy"),
    ]
    CSS = """
    DetailScreen {
        align: center middle;
        background: $background 80%;
    }
    #detail-dialog {
        width: 85%;
        height: 85%;
        max-width: 110;
        padding: 1 2;
        border: thick $primary;
        background: $surface;
    }
    #detail-title {
        height: 2;
        text-style: bold;
        color: $accent;
    }
    #detail-summary {
        height: auto;
        margin-bottom: 1;
        padding: 0 1;
        background: $panel;
        border-left: solid $primary;
    }
    #detail-message-title {
        height: 1;
        margin-top: 1;
        text-style: bold;
        color: $text-muted;
    }
    #detail-message {
        height: auto;
        max-height: 12;
        overflow: auto;
        padding: 1;
        border-left: thick $accent;
        background: $panel;
    }
    #detail-fields-title {
        height: 1;
        margin-top: 1;
        text-style: bold;
        color: $text-muted;
    }
    #detail-fields {
        height: 1fr;
        overflow: auto;
        background: $panel;
        padding: 0 1;
    }
    #detail-hint {
        height: 1;
        margin-top: 1;
        color: $text-muted;
        text-align: right;
    }
    """

    def __init__(self, entry: LogEntry) -> None:
        super().__init__()
        self.entry = entry

    def compose(self) -> ComposeResult:
        timestamp = (
            self.entry.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.entry.timestamp else "—"
        )
        lvl_key = (self.entry.level or "").upper()
        if lvl_key in LEVEL_BADGES:
            text_val, style_val = LEVEL_BADGES[lvl_key]
            level_fmt = f"[{style_val}] {text_val} [/]"
        else:
            level_fmt = f"[dim]{self.entry.level or '—'}[/dim]"

        summary = (
            f"[b]Time[/b]  {timestamp}    "
            f"[b]Level[/b]  {level_fmt}    "
            f"[b]Service[/b]  [bold cyan]{self.entry.service or '—'}[/]    "
            f"[b]Source[/b]  [magenta]{self.entry.source}[/]"
        )
        fields = self.entry.fields or {"raw": self.entry.raw or self.entry.message}
        with Vertical(id="detail-dialog"):
            yield Label("🔍 Log entry details", id="detail-title")
            yield Label(summary, id="detail-summary")
            yield Label("MESSAGE / STACKTRACE", id="detail-message-title")
            yield Static(self.entry.message, id="detail-message")
            yield Label(f"STRUCTURED FIELDS ({len(fields)})", id="detail-fields-title")
            yield Static(
                Syntax(
                    json.dumps(fields, indent=2, default=str),
                    "json",
                    theme="monokai",
                    word_wrap=True,
                ),
                id="detail-fields",
            )
            yield Label("[b]c[/b] copy raw  ·  [b]esc / q[/b] close", id="detail-hint")

    def action_copy_raw(self) -> None:
        content = self.entry.raw or self.entry.message
        self.app.copy_to_clipboard(content)
        self.notify("Log raw content copied to clipboard!", title="Copied", severity="information")

    async def action_dismiss(self, result: None = None) -> None:
        self.dismiss(result)


class ExportScreen(ModalScreen[None]):
    BINDINGS = [
        Binding("escape", "dismiss", "Cancel"),
        Binding("q", "dismiss", "Cancel"),
    ]
    CSS = """
    ExportScreen {
        align: center middle;
        background: $background 80%;
    }
    #export-dialog {
        width: 60;
        height: auto;
        padding: 1 2;
        border: thick $primary;
        background: $surface;
    }
    #export-title {
        height: 2;
        text-style: bold;
        color: $accent;
    }
    #export-input {
        margin: 1 0;
    }
    #export-hint {
        height: 1;
        color: $text-muted;
        text-align: right;
    }
    """

    def __init__(self, entries: list[LogEntry]) -> None:
        super().__init__()
        self.entries_to_export = entries

    def compose(self) -> ComposeResult:
        with Vertical(id="export-dialog"):
            yield Label(
                f"💾 Export logs ({len(self.entries_to_export)} entries)",
                id="export-title",
            )
            yield Label("Formats supported: .jsonl, .json, .csv")
            yield Input(value="export.jsonl", placeholder="Enter filename...", id="export-input")
            yield Label("[b]enter[/b] save  ·  [b]esc / q[/b] cancel", id="export-hint")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        path_str = event.value.strip()
        if not path_str:
            self.dismiss()
            return
        dest = Path(path_str)
        try:
            count = export_logs(self.entries_to_export, dest)
            self.app.notify(
                f"Exported {count} logs to {dest.name}!",
                title="Export complete",
                severity="information",
            )
        except Exception as err:
            self.app.notify(f"Export failed: {err}", title="Error", severity="error")
        self.dismiss()

    async def action_dismiss(self, result: None = None) -> None:
        self.dismiss(result)


class HelpScreen(ModalScreen[None]):
    BINDINGS = [
        Binding("escape", "dismiss", "Back"),
        Binding("q", "dismiss", "Back"),
        Binding("?", "dismiss", "Back"),
    ]
    CSS = """
    HelpScreen {
        align: center middle;
        background: $background 80%;
    }
    #help-dialog {
        width: 66;
        height: auto;
        padding: 1 2;
        border: thick $primary;
        background: $surface;
    }
    #help-title {
        height: 2;
        text-style: bold;
        color: $accent;
    }
    #help-keys {
        height: auto;
    }
    #help-hint {
        height: 2;
        padding-top: 1;
        color: $text-muted;
        text-align: right;
    }
    """

    def compose(self) -> ComposeResult:
        keys = (
            "[bold cyan]Navigation[/bold cyan]\n"
            "  [b]↑ / ↓  j / k[/b]     Move selection up / down\n"
            "  [b]g / G[/b]             Jump to first / last log\n"
            "  [b]enter[/b]             Inspect entry details & JSON\n\n"
            "[bold cyan]Filtering & Search[/bold cyan]\n"
            "  [b]/[/b]                 Search logs or structured query\n"
            "  [b]l[/b]                 Cycle level filter ([dim]ALL → INFO+ → WARN+[/dim])\n"
            "  [b]0..4[/b]              Jump to level ([dim]0:ALL 1:DBG 2:INF 3:WRN 4:ERR[/dim])\n"
            "  [b]s[/b]                 Filter by source file\n"
            "  [b]e[/b]                 Export visible logs to file (.jsonl, .json, .csv)\n\n"
            "[bold cyan]Streaming & Control[/bold cyan]\n"
            "  [b]space[/b]             Pause / resume streaming\n"
            "  [b]f[/b]                 Toggle auto-follow ([dim]scrolls to new logs[/dim])\n"
            "  [b]?[/b]                 Toggle this help dialog\n"
            "  [b]q[/b]                 Quit LogTUI"
        )
        with Vertical(id="help-dialog"):
            yield Label("⌨ Keyboard shortcuts", id="help-title")
            yield Label(keys, id="help-keys")
            yield Label("[b]esc / ? / q[/b]  close", id="help-hint")

    async def action_dismiss(self, result: None = None) -> None:
        self.dismiss(result)


class LogTuiApp(App[None]):
    TITLE = "LogTUI"
    SUB_TITLE = "Live log explorer"
    CSS = """
    Screen {
        background: $background;
    }
    #workspace {
        height: 1fr;
    }
    #sidebar {
        width: 28;
        min-width: 22;
        height: 1fr;
        border-right: solid $primary-darken-2;
        background: $surface;
    }
    #sources-title {
        height: 1;
        padding: 0 1;
        color: $accent;
        text-style: bold;
    }
    #sources {
        height: auto;
        padding: 0 1;
        margin-top: 1;
    }
    .source-row {
        height: 1;
        padding: 0 1;
        color: $text;
    }
    .source-row:hover {
        background: $panel;
        color: $accent;
    }
    #levels-summary {
        height: auto;
        padding: 0 1;
        margin-top: 1;
        border-top: solid $panel-lighten-2;
    }
    #levels-title {
        height: 1;
        padding-top: 1;
        color: $text-muted;
        text-style: bold;
    }
    .level-row {
        height: 1;
        padding: 0 1;
    }
    #lvl-bar {
        height: 1;
        padding: 0 1;
        margin-top: 1;
    }
    #sidebar-info {
        height: 3;
        dock: bottom;
        padding: 0 1;
        border-top: solid $panel-lighten-2;
        color: $text-muted;
    }
    #content {
        width: 1fr;
        height: 1fr;
    }
    #table-title-bar {
        height: 1;
        padding: 0 1;
        background: $surface;
        border-bottom: solid $panel-lighten-2;
    }
    #table-title {
        width: 1fr;
        text-style: bold;
    }
    #table-filters {
        width: auto;
        text-align: right;
    }
    #logs {
        height: 1fr;
        border: none;
    }
    #search-input {
        display: none;
        height: 3;
        border: tall $accent;
        background: $surface;
    }
    #search-input.visible {
        display: block;
    }
    #status-bar {
        height: 1;
        padding: 0 1;
        background: $panel;
        color: $text-muted;
    }
    #stream-state {
        width: 1fr;
    }
    #stream-count {
        width: auto;
        text-align: right;
    }
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
        Binding("f", "toggle_follow", "Follow", show=False),
        Binding("l", "cycle_level", "Level", show=False),
        Binding("s", "cycle_source", "Source", show=False),
        Binding("e", "export", "Export", show=False),
        Binding("g", "scroll_top", "Top", show=False),
        Binding("G", "scroll_bottom", "Bottom", show=False),
        Binding("0", "set_level_all", "All levels", show=False),
        Binding("1", "set_level_debug", "Debug+", show=False),
        Binding("2", "set_level_info", "Info+", show=False),
        Binding("3", "set_level_warn", "Warn+", show=False),
        Binding("4", "set_level_error", "Error+", show=False),
    ]

    def __init__(
        self,
        sources: Sequence[LogSource],
        buffer_size: int = 10_000,
        initial_query: str = "",
        initial_level: int = 0,
    ) -> None:
        super().__init__()
        self.sources = list(sources)
        self.entries: RingBuffer[LogEntry] = RingBuffer(buffer_size)
        self.parser = AutoDetectParser()
        self.paused = False
        self.follow = True
        self._pending_count = 0
        self._source_counts: Counter[str] = Counter()
        self._level_counts: Counter[str] = Counter()
        self._source_errors: dict[str, str] = {}
        self.search_query = initial_query
        self._compiled_query = Query(initial_query) if initial_query else None
        self.level_filter_index = initial_level
        self.active_source_index = -1
        self._next_id = 0
        self._tasks: list[asyncio.Task[Any]] = []
        self._pending_rows: list[LogEntry] = []
        self._needs_refresh = False

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
                with Vertical(id="levels-summary"):
                    yield Label("LEVELS", id="levels-title")
                    yield Label("● ERR   [dim]0[/dim]", id="lvl-error", classes="level-row")
                    yield Label("▲ WARN  [dim]0[/dim]", id="lvl-warn", classes="level-row")
                    yield Label("ℹ INFO  [dim]0[/dim]", id="lvl-info", classes="level-row")
                    yield Label("· DEBUG [dim]0[/dim]", id="lvl-debug", classes="level-row")
                    yield Label("", id="lvl-bar")
                yield Label(
                    f"Buffer  [b]{self.entries.capacity:,}[/b]\n[dim]entries max[/dim]",
                    id="sidebar-info",
                )
            with Vertical(id="content"):
                with Horizontal(id="table-title-bar"):
                    yield Label("Live events", id="table-title")
                    yield Label("", id="table-filters")
                yield DataTable(cursor_type="row", zebra_stripes=True, id="logs")
                yield Input(
                    placeholder="Search logs or query (e.g. level:error service:api)...",
                    id="search-input",
                )
                with Horizontal(id="status-bar"):
                    yield Label(
                        "[bold green]● LIVE[/bold green]  Following files", id="stream-state"
                    )
                    yield Label("0 events", id="stream-count")
        yield Footer()

    def _query_main(self, selector: str, expect_type: type[W]) -> W:
        screen = self.screen_stack[0] if self.screen_stack else self.screen
        return screen.query_one(selector, expect_type)

    async def on_mount(self) -> None:
        table = self._query_main("#logs", DataTable)
        table.add_columns("TIME", "LEVEL", "SERVICE", "SOURCE", "MESSAGE")
        table.focus()
        self.set_interval(0.025, self._flush_ui, pause=False)
        for source in self.sources:
            task = asyncio.create_task(self._consume(source))
            task.add_done_callback(partial(self._source_done, source_name=source.name))
            self._tasks.append(task)

    async def _consume(self, source: LogSource) -> None:
        async for line in source.lines():
            # Handle multi-line continuation / stacktraces
            if len(self.entries) > 0 and is_continuation_line(line):
                last_entry = self.entries[-1]
                if last_entry.source == source.name:
                    merge_continuation(last_entry, line)
                    self._needs_refresh = True
                    continue

            entry = self.parser.parse(line, source.name)
            entry.id = self._next_id
            self._next_id += 1
            self.entries.append(entry)
            self._source_counts[source.name] += 1
            lvl = (entry.level or "OTHER").upper()
            self._level_counts[lvl] += 1

            if self.paused:
                self._pending_count += 1
            elif self._matches_filters(entry):
                self._pending_rows.append(entry)
            self._needs_refresh = True

            # Rapid feedback for initial lines or tests
            if self.is_running and len(self._pending_rows) <= 5:
                self._flush_ui()

    def _source_done(self, task: asyncio.Task[Any], source_name: str) -> None:
        if task.cancelled():
            return
        error = task.exception()
        if error is not None:
            self._source_errors[source_name] = str(error)
            self._refresh_chrome()

    def _flush_ui(self) -> None:
        if not self.is_running or not self.screen_stack:
            return
        if not self._pending_rows and not self._needs_refresh:
            return

        try:
            table = self._query_main("#logs", DataTable)
        except Exception:
            return

        if self._pending_rows:
            batch = self._pending_rows
            self._pending_rows = []
            for entry in batch:
                self._add_row_to_table(table, entry)

            overflow = table.row_count - self.entries.capacity
            if overflow > 0:
                for key in list(table.rows)[:overflow]:
                    table.remove_row(key)

            if self.follow and table.row_count:
                table.move_cursor(row=table.row_count - 1)

        if self._needs_refresh:
            self._refresh_chrome()
            self._needs_refresh = False

    def _add_row(self, entry: LogEntry) -> None:
        if not self.is_running or not self.screen_stack:
            return
        try:
            table = self._query_main("#logs", DataTable)
        except Exception:
            return
        self._add_row_to_table(table, entry)
        overflow = table.row_count - self.entries.capacity
        if overflow > 0:
            for key in list(table.rows)[:overflow]:
                table.remove_row(key)
        if self.follow and table.row_count:
            table.move_cursor(row=table.row_count - 1)

    def _add_row_to_table(self, table: DataTable[Any], entry: LogEntry) -> None:
        # 1. TIME
        if entry.timestamp:
            if entry.timestamp.microsecond:
                t_str = (
                    entry.timestamp.strftime("%H:%M:%S.")
                    + f"{entry.timestamp.microsecond // 1000:03d}"
                )
            else:
                t_str = entry.timestamp.strftime("%H:%M:%S")
            time_cell = Text(t_str, style="#64748b")
        else:
            time_cell = Text("—", style="dim")

        # 2. LEVEL
        lvl_key = (entry.level or "").upper()
        if lvl_key in LEVEL_BADGES:
            text_val, style_val = LEVEL_BADGES[lvl_key]
            level_cell = Text(f" {text_val} ", style=style_val)
        else:
            level_cell = Text(f" {lvl_key or '—':<5} ", style="dim")

        # 3. SERVICE
        service_cell = Text(entry.service or "—", style="bold #0ea5e9" if entry.service else "dim")

        # 4. SOURCE
        source_disp = self._display_name(entry.source)
        source_cell = Text(source_disp, style="#8b5cf6")

        # 5. MESSAGE (show first line if multiline in table)
        first_line = entry.message.split("\n", 1)[0]
        if self.search_query and self.search_query in first_line.casefold():
            msg_cell = Text()
            pos = 0
            q_len = len(self.search_query)
            msg_lower = first_line.casefold()
            while True:
                idx = msg_lower.find(self.search_query, pos)
                if idx == -1:
                    msg_cell.append(first_line[pos:])
                    break
                msg_cell.append(first_line[pos:idx])
                msg_cell.append(first_line[idx : idx + q_len], style="bold black on #facc15")
                pos = idx + q_len
        elif lvl_key in ("ERROR", "CRITICAL", "FATAL"):
            msg_cell = Text(first_line, style="#fca5a5")
        elif lvl_key in ("WARN", "WARNING"):
            msg_cell = Text(first_line, style="#fef08a")
        else:
            msg_cell = Text(first_line)

        table.add_row(
            time_cell,
            level_cell,
            service_cell,
            source_cell,
            msg_cell,
            key=str(entry.id),
        )

    def _refresh_chrome(self) -> None:
        if not self.is_running or not self.screen_stack:
            return
        pending = f" · {self._pending_count:,} pending" if self._pending_count else ""
        if self._source_errors:
            err = next(iter(self._source_errors.values()))
            state = f"[bold red]● SOURCE ERROR[/bold red]  {err}"
        elif self.paused:
            state = f"[bold yellow]❚❚ PAUSED[/bold yellow]{pending}"
        elif self.follow:
            state = "[bold green]● LIVE[/bold green]  Following files"
        else:
            state = "[bold cyan]● LIVE[/bold cyan]  [dim](scroll paused · 'f' to follow)[/dim]"

        try:
            self._query_main("#stream-state", Label).update(state)

            count = len(self.entries)
            if self.search_query or self.level_filter_index > 0 or self.active_source_index >= 0:
                visible = self._query_main("#logs", DataTable).row_count
                counter = f"{visible:,} of {count:,} events"
            else:
                counter = f"{count:,} event{'s' if count != 1 else ''}"
            self._query_main("#stream-count", Label).update(counter)

            # Update top toolbar filter tags
            lvl_filter = LEVEL_FILTERS[self.level_filter_index]
            lvl_tag = (
                f"[bold white on #1e3a8a] LVL: {lvl_filter} [/]"
                if lvl_filter != "ALL"
                else "[dim]LVL: ALL[/dim]"
            )
            if self.active_source_index >= 0:
                src_name = self._display_name(self.sources[self.active_source_index].name)
                src_tag = f"[bold white on #0f766e] SRC: {src_name} [/]"
            else:
                src_tag = "[dim]SRC: ALL[/dim]"
            follow_tag = "[bold #4ade80]FOLLOW: ON[/]" if self.follow else "[dim]FOLLOW: OFF[/dim]"
            search_tag = (
                f'[bold black on #facc15] 🔍 "{self.search_query}" [/]' if self.search_query else ""
            )
            filters_markup = f"{search_tag}  {lvl_tag}  {src_tag}  {follow_tag}".strip()
            self._query_main("#table-filters", Label).update(filters_markup)

            # Update sources list in sidebar
            for index, source in enumerate(self.sources):
                source_name = source.name
                is_active_filter = (
                    self.active_source_index >= 0
                    and self.sources[self.active_source_index].name == source_name
                )
                if source_name in self._source_errors:
                    marker = "[red]●[/red]"
                elif is_active_filter:
                    marker = "[bold cyan]▶[/bold cyan]"
                else:
                    marker = (
                        "[green]●[/green]" if self._source_counts[source_name] else "[dim]○[/dim]"
                    )
                total = self._source_counts[source_name]
                name_disp = self._display_name(source_name)
                if is_active_filter:
                    self._query_main(f"#source-{index}", Label).update(
                        f"{marker} [bold cyan]{name_disp}[/bold cyan] [b]{total:,}[/b]"
                    )
                else:
                    self._query_main(f"#source-{index}", Label).update(
                        f"{marker} {name_disp} [dim]{total:,}[/dim]"
                    )

            # Update level summary counts in sidebar
            err_total = (
                self._level_counts["ERROR"]
                + self._level_counts["CRITICAL"]
                + self._level_counts["FATAL"]
            )
            warn_total = self._level_counts["WARN"] + self._level_counts["WARNING"]
            info_total = self._level_counts["INFO"]
            debug_total = self._level_counts["DEBUG"] + self._level_counts["TRACE"]

            self._query_main("#lvl-error", Label).update(
                f"[bold red]● ERR [/bold red]  [b]{err_total:,}[/b]"
                if err_total
                else "[dim]● ERR   0[/dim]"
            )
            self._query_main("#lvl-warn", Label).update(
                f"[bold yellow]▲ WARN[/bold yellow]  [b]{warn_total:,}[/b]"
                if warn_total
                else "[dim]▲ WARN  0[/dim]"
            )
            self._query_main("#lvl-info", Label).update(
                f"[bold green]ℹ INFO[/bold green]  [b]{info_total:,}[/b]"
                if info_total
                else "[dim]ℹ INFO  0[/dim]"
            )
            self._query_main("#lvl-debug", Label).update(
                f"[cyan]· DEBUG[/cyan] [b]{debug_total:,}[/b]"
                if debug_total
                else "[dim]· DEBUG 0[/dim]"
            )

            # Visual mini-distribution bar
            total_logs = err_total + warn_total + info_total + debug_total
            if total_logs > 0:
                width = 18
                err_w = round((err_total / total_logs) * width)
                warn_w = round((warn_total / total_logs) * width)
                info_w = round((info_total / total_logs) * width)
                dbg_w = max(0, width - (err_w + warn_w + info_w))
                bar_text = (
                    f"[bold red]{'█' * err_w}[/bold red]"
                    f"[bold yellow]{'█' * warn_w}[/bold yellow]"
                    f"[bold green]{'█' * info_w}[/bold green]"
                    f"[cyan]{'█' * dbg_w}[/cyan]"
                )
                self._query_main("#lvl-bar", Label).update(bar_text)
            else:
                self._query_main("#lvl-bar", Label).update("[dim]──────────────────[/dim]")

            # Update buffer info
            buf_len = len(self.entries)
            buf_cap = self.entries.capacity
            pct = (buf_len / buf_cap) * 100 if buf_cap else 0
            self._query_main("#sidebar-info", Label).update(
                f"Buffer  [b]{buf_len:,}[/b] / {buf_cap:,}\n[dim]{pct:.0f}% memory usage[/dim]"
            )
        except Exception:
            return

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
        if not self.is_running or not self.screen_stack:
            return
        self._pending_rows = []
        try:
            table = self._query_main("#logs", DataTable)
        except Exception:
            return
        table.clear()
        for entry in self.entries:
            if self._matches_filters(entry):
                self._add_row_to_table(table, entry)
        if self.follow and table.row_count:
            table.move_cursor(row=table.row_count - 1)

    def _matches_filters(self, entry: LogEntry) -> bool:
        if self.active_source_index >= 0:
            selected_source = self.sources[self.active_source_index].name
            if entry.source != selected_source:
                return False

        filter_name = LEVEL_FILTERS[self.level_filter_index]
        if filter_name != "ALL":
            min_weight = {
                "DEBUG+": 10,
                "INFO+": 20,
                "WARN+": 30,
                "ERROR+": 40,
            }.get(filter_name, 0)
            entry_level = (entry.level or "").upper()
            weight = LEVEL_WEIGHTS.get(entry_level, 0)
            if weight < min_weight:
                return False

        return self._matches_search(entry)

    def _matches_search(self, entry: LogEntry) -> bool:
        if not self.search_query:
            return True

        if self._compiled_query is not None:
            return self._compiled_query.matches(entry)

        query = self.search_query
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

    def action_search(self) -> None:
        with suppress(Exception):
            search = self._query_main("#search-input", Input)
            search.add_class("visible")
            search.value = self.search_query
            search.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "search-input":
            return
        self.search_query = event.value.strip().casefold()
        self._compiled_query = Query(self.search_query) if self.search_query else None
        event.input.remove_class("visible")
        self._rebuild_table()
        self._refresh_chrome()
        with suppress(Exception):
            self._query_main("#logs", DataTable).focus()

    def action_clear_search(self) -> None:
        with suppress(Exception):
            search = self._query_main("#search-input", Input)
            if search.has_class("visible"):
                search.remove_class("visible")
                self._query_main("#logs", DataTable).focus()
                return
            if self.search_query:
                self.search_query = ""
                self._compiled_query = None
                search.value = ""
                self._rebuild_table()
                self._refresh_chrome()

    def action_cursor_down(self) -> None:
        with suppress(Exception):
            table = self._query_main("#logs", DataTable)
            table.action_cursor_down()
            if table.cursor_row >= table.row_count - 1:
                self.follow = True
                self._refresh_chrome()

    def action_cursor_up(self) -> None:
        with suppress(Exception):
            table = self._query_main("#logs", DataTable)
            table.action_cursor_up()
            if self.follow:
                self.follow = False
                self._refresh_chrome()

    def action_scroll_top(self) -> None:
        with suppress(Exception):
            table = self._query_main("#logs", DataTable)
            if table.row_count:
                table.move_cursor(row=0)
                self.follow = False
                self._refresh_chrome()

    def action_scroll_bottom(self) -> None:
        with suppress(Exception):
            table = self._query_main("#logs", DataTable)
            if table.row_count:
                table.move_cursor(row=table.row_count - 1)
                self.follow = True
                self._refresh_chrome()

    def action_toggle_follow(self) -> None:
        self.follow = not self.follow
        with suppress(Exception):
            table = self._query_main("#logs", DataTable)
            if self.follow and table.row_count:
                table.move_cursor(row=table.row_count - 1)
        self._refresh_chrome()

    def action_cycle_level(self) -> None:
        self.level_filter_index = (self.level_filter_index + 1) % len(LEVEL_FILTERS)
        self._rebuild_table()
        self._refresh_chrome()

    def action_set_level_all(self) -> None:
        self.level_filter_index = 0
        self._rebuild_table()
        self._refresh_chrome()

    def action_set_level_debug(self) -> None:
        self.level_filter_index = 1
        self._rebuild_table()
        self._refresh_chrome()

    def action_set_level_info(self) -> None:
        self.level_filter_index = 2
        self._rebuild_table()
        self._refresh_chrome()

    def action_set_level_warn(self) -> None:
        self.level_filter_index = 3
        self._rebuild_table()
        self._refresh_chrome()

    def action_set_level_error(self) -> None:
        self.level_filter_index = 4
        self._rebuild_table()
        self._refresh_chrome()

    def action_cycle_source(self) -> None:
        if not self.sources:
            return
        if self.active_source_index < len(self.sources) - 1:
            self.active_source_index += 1
        else:
            self.active_source_index = -1
        self._rebuild_table()
        self._refresh_chrome()

    def action_export(self) -> None:
        matching = [e for e in self.entries if self._matches_filters(e)]
        self.push_screen(ExportScreen(matching))

    def on_click(self, event: events.Click) -> None:
        for index, _ in enumerate(self.sources):
            with suppress(Exception):
                lbl = self._query_main(f"#source-{index}", Label)
                if event.widget == lbl:
                    if self.active_source_index == index:
                        self.active_source_index = -1
                    else:
                        self.active_source_index = index
                    self._rebuild_table()
                    self._refresh_chrome()
                    return

    def action_details(self) -> None:
        with suppress(Exception):
            table = self._query_main("#logs", DataTable)
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

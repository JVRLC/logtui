import asyncio
import sys
from pathlib import Path
from typing import Annotated

import typer

from logtui.export import export_logs
from logtui.models import LogEntry
from logtui.parsing import AutoDetectParser
from logtui.parsing.query import LEVEL_WEIGHTS, Query
from logtui.sources import DockerSource, FileSource, StdinSource
from logtui.sources.base import LogSource
from logtui.tui import LogTuiApp

app = typer.Typer(
    add_completion=False,
    help="A fast terminal UI for exploring and filtering logs.",
    no_args_is_help=True,
)


async def _run_headless(
    sources: list[LogSource],
    level: str | None,
    query_str: str | None,
    jsonl: bool,
    export_path: Path | None,
) -> None:
    parser = AutoDetectParser()
    query = Query(query_str) if query_str else None
    min_weight = LEVEL_WEIGHTS.get(level.upper(), 0) if level else 0
    collected: list[LogEntry] = []

    for source in sources:
        async for line in source.lines():
            entry = parser.parse(line, source.name)
            if min_weight:
                entry_weight = LEVEL_WEIGHTS.get((entry.level or "").upper(), 0)
                if entry_weight < min_weight:
                    continue
            if query and not query.matches(entry):
                continue

            if export_path:
                collected.append(entry)
            elif jsonl:
                sys.stdout.write(entry.model_dump_json() + "\n")
                sys.stdout.flush()
            else:
                ts = entry.timestamp.strftime("%H:%M:%S") if entry.timestamp else "—"
                lvl = entry.level or "—"
                sys.stdout.write(f"{ts} [{lvl}] {entry.source}: {entry.message}\n")
                sys.stdout.flush()

    if export_path:
        count = export_logs(collected, export_path)
        sys.stderr.write(f"Exported {count:,} log entries to {export_path}\n")


@app.command()
def main(
    files: Annotated[
        list[str],
        typer.Argument(help="Log files to follow, docker:container, or - for stdin"),
    ],
    buffer_size: Annotated[
        int, typer.Option("--buffer-size", min=1, help="Maximum logs kept in memory")
    ] = 10_000,
    level: Annotated[
        str | None,
        typer.Option("--level", "-l", help="Minimum log level (DEBUG, INFO, WARN, ERROR)"),
    ] = None,
    query: Annotated[
        str | None,
        typer.Option("--query", "-q", help="Search or structured query"),
    ] = None,
    headless: Annotated[
        bool,
        typer.Option("--headless", help="Run in headless mode without TUI"),
    ] = False,
    jsonl: Annotated[
        bool,
        typer.Option("--jsonl", help="Output parsed logs as JSONL to stdout"),
    ] = False,
    export: Annotated[
        Path | None,
        typer.Option("--export", "-e", help="Export filtered logs to file (.jsonl, .json, .csv)"),
    ] = None,
    wait: Annotated[
        bool,
        typer.Option("--wait", "-w", help="Wait for missing files to be created"),
    ] = False,
    follow: Annotated[
        bool | None,
        typer.Option("--follow", "-f", help="Follow file for new lines"),
    ] = None,
) -> None:
    """Open one or more log sources."""
    file_paths = [Path(val) for val in files if val != "-" and not val.startswith("docker:")]
    if not wait:
        missing = [path for path in file_paths if not path.is_file()]
        if missing:
            names = ", ".join(str(path) for path in missing)
            raise typer.BadParameter(f"file not found: {names}")

    if files.count("-") > 1:
        raise typer.BadParameter("stdin may only be specified once")

    is_headless = headless or jsonl or export is not None
    should_follow = follow if follow is not None else not is_headless

    sources: list[LogSource] = []
    for val in files:
        if val == "-":
            sources.append(StdinSource())
        elif val.startswith("docker:"):
            sources.append(DockerSource(val.removeprefix("docker:")))
        else:
            sources.append(FileSource(Path(val), wait_for_creation=wait, follow=should_follow))

    if is_headless:
        asyncio.run(
            _run_headless(
                sources=sources,
                level=level,
                query_str=query,
                jsonl=jsonl,
                export_path=export,
            )
        )
    else:
        level_index = 0
        if level:
            lvl_upper = level.upper()
            from logtui.tui.app import LEVEL_FILTERS

            for idx, name in enumerate(LEVEL_FILTERS):
                if lvl_upper in name:
                    level_index = idx
                    break

        app_instance = LogTuiApp(
            sources=sources,
            buffer_size=buffer_size,
            initial_query=query or "",
            initial_level=level_index,
        )
        app_instance.run()


if __name__ == "__main__":
    app()

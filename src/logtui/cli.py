from pathlib import Path
from typing import Annotated

import typer

from logtui.sources import FileSource, StdinSource
from logtui.tui import LogTuiApp

app = typer.Typer(
    add_completion=False,
    help="A fast terminal UI for exploring and filtering logs.",
    no_args_is_help=True,
)


@app.command()
def main(
    files: Annotated[list[str], typer.Argument(help="Log files to follow, or - for stdin")],
    buffer_size: Annotated[
        int, typer.Option("--buffer-size", min=1, help="Maximum logs kept in memory")
    ] = 10_000,
) -> None:
    """Open one or more local log files."""
    file_paths = [Path(value) for value in files if value != "-"]
    missing = [path for path in file_paths if not path.is_file()]
    if missing:
        names = ", ".join(str(path) for path in missing)
        raise typer.BadParameter(f"file not found: {names}")
    if files.count("-") > 1:
        raise typer.BadParameter("stdin may only be specified once")
    sources = [StdinSource() if value == "-" else FileSource(Path(value)) for value in files]
    LogTuiApp(sources, buffer_size).run()


if __name__ == "__main__":
    app()

from pathlib import Path
from typing import Annotated

import typer

from logtui.tui import LogTuiApp

app = typer.Typer(
    add_completion=False,
    help="A fast terminal UI for exploring and filtering logs.",
    no_args_is_help=True,
)


@app.command()
def main(
    files: Annotated[list[Path], typer.Argument(help="Log files to read and follow")],
    buffer_size: Annotated[
        int, typer.Option("--buffer-size", min=1, help="Maximum logs kept in memory")
    ] = 10_000,
) -> None:
    """Open one or more local log files."""
    missing = [path for path in files if not path.is_file()]
    if missing:
        names = ", ".join(str(path) for path in missing)
        raise typer.BadParameter(f"file not found: {names}")
    LogTuiApp(files, buffer_size).run()


if __name__ == "__main__":
    app()

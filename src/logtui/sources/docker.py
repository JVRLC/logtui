import asyncio
import shutil
from collections.abc import AsyncIterator


class DockerSource:
    """Read and follow logs from a Docker container."""

    def __init__(self, container: str, tail: int = 200) -> None:
        self.container = container
        self.tail = tail
        self.name = f"docker:{container}"

    async def lines(self) -> AsyncIterator[str]:
        if not shutil.which("docker"):
            raise RuntimeError("docker binary not found in PATH")

        process = await asyncio.create_subprocess_exec(
            "docker",
            "logs",
            "-f",
            f"--tail={self.tail}",
            self.container,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        try:
            if process.stdout is None:
                return
            while line_bytes := await process.stdout.readline():
                yield line_bytes.decode("utf-8", errors="replace")
        finally:
            if process.returncode is None:
                try:
                    process.terminate()
                    await process.wait()
                except ProcessLookupError:
                    pass

# Contributing to LogTUI

Thank you for helping improve LogTUI. Bug reports, documentation fixes, tests,
and focused feature contributions are welcome.

## Before opening an issue

- Search existing issues to avoid duplicates.
- Include your operating system and Python version.
- For bugs, provide a minimal log sample with secrets removed and the exact
  command used to reproduce the problem.
- Security vulnerabilities must be reported according to [SECURITY.md](SECURITY.md),
  not through a public issue.

## Development setup

LogTUI requires Python 3.12 or newer.

```bash
git clone https://github.com/JVRLC/logtui.git
cd logtui
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

Run the quality checks before submitting a change:

```bash
pytest
ruff check .
ruff format --check .
mypy src
```

## Pull requests

- Keep changes small and focused.
- Add tests for behavior changes and bug fixes.
- Update the README or changelog when user-facing behavior changes.
- Do not introduce external services into the local-first core.
- Use clear commit messages written in the imperative mood.

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

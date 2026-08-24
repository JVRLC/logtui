# Changelog

All notable changes to LogTUI will be documented in this file. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the
project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial Typer command-line interface.
- Live following of one or more local log files.
- JSONL, Python log, and plain-text parsing.
- Normalized Pydantic log model and bounded in-memory ring buffer.
- Textual table with pause/resume and structured detail view.
- Unit tests, static analysis, formatting, and continuous integration.
- Responsive project website and automated GitHub Pages deployment.
- Standard input support for Docker, Kubernetes, journald, and other pipelines.
- Interactive text search across normalized and dynamic log fields.
- Coverage reporting, dependency auditing, and distribution builds in CI.

### Changed

- Redesigned the TUI with a source sidebar, live counters, colored levels,
  keyboard help, and a structured detail dialog.
- Made file following resilient to truncation and atomic replacement.
- Bounded paused streams by the configured ring-buffer capacity and surfaced
  asynchronous source failures in the interface.

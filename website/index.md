---
layout: home

hero:
  name: "LogTUI,"
  text: "A TUI to explore live logs"
  tagline: Read, follow and inspect local logs without leaving your terminal.
  image:
    src: /logo.svg
    alt: LogTUI
  actions:
    - theme: brand
      text: Getting started
      link: /getting-started/

features:
  - icon: ⚡
    title: Real-time + Multi-file
    details: Follow new entries and explore several local log files in one unified stream.
    link: /multiple-sources/
  - icon: 🔎
    title: Structured inspection
    details: Automatically normalize JSONL, Python logs and unknown plain-text formats.
    link: /log-formats/
  - icon: 🖥️
    title: Local by default
    details: Start with one command. No server, database or external service is required.
    link: /what-is-logtui/
  - icon: ⌨️
    title: Keyboard first
    details: Navigate, pause and inspect entries through fast, discoverable keybindings.
    link: /keybindings/
---

<p class="home-intro">
Start immediately with <code>logtui app.log</code>, or combine sources with
<code>logtui api.log worker.log</code>.
</p>

<img class="terminal-preview" src="/terminal-preview.svg" alt="LogTUI displaying live structured logs in a terminal" />

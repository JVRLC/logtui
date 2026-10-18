---
layout: home

hero:
  name: "LogTUI"
  text: "The live log explorer for your terminal"
  tagline: Tail, filter and inspect multi-file logs, Docker containers and JSON traces with instant queries and zero configuration.
  image:
    src: /logo.svg
    alt: LogTUI
  actions:
    - theme: brand
      text: Get Started →
      link: /getting-started/
    - theme: alt
      text: Keybindings
      link: /keybindings/
    - theme: alt
      text: View on GitHub ↗
      link: https://github.com/JVRLC/logtui

features:
  - icon: ⚡
    title: Real-time Multi-Source
    details: Follow local files, Docker containers (docker:name) and stdin pipes simultaneously in a unified high-performance stream.
    link: /multiple-sources/
  - icon: 🔎
    title: Structured Query Engine
    details: Filter on the fly with level:error, service:api, status:>=500, negations -key:val, and full-text searches.
    link: /log-formats/
  - icon: 🧵
    title: Stacktrace Aggregation
    details: Automatic multi-line continuation grouping for Python, Java, and Go exceptions with automatic ERROR elevation.
    link: /log-formats/
  - icon: 🔍
    title: Instant Deep Inspection
    details: Press Enter on any log entry to open syntax-highlighted JSON, formatted fields, and copy raw logs with a single key.
    link: /keybindings/
  - icon: 💾
    title: Quick Export (JSONL / CSV)
    details: Export your current filtered view to .jsonl, .json or .csv directly within the TUI or via headless CLI mode.
    link: /getting-started/
  - icon: 🖥️
    title: 100% Local & Zero Config
    details: Powered by Textual and Rich. No background daemon, no Elasticsearch, no database, no telemetry.
    link: /what-is-logtui/
---

<div class="quick-install">
  <span class="prompt">$</span>
  <code>pipx install git+https://github.com/JVRLC/logtui.git</code>
</div>

<div class="terminal-showcase">
  <img class="terminal-preview" src="/terminal-preview.svg" alt="LogTUI displaying live structured logs in a terminal with distribution bar, badges and sidebar" />
</div>

<div class="showcase-section">
  <div class="showcase-header">
    <h2>Built for developers, SREs & terminal lovers</h2>
    <p>Everything you need to diagnose issues in local development and production servers.</p>
  </div>

  <div class="command-grid">
    <div class="command-card">
      <h3>Multi-File Streaming</h3>
      <p>Aggregate logs across different microservices into a single correlated view.</p>
      <pre><code>logtui api.log worker.log nginx.log</code></pre>
    </div>

    <div class="command-card">
      <h3>Docker Container Logs</h3>
      <p>Directly attach to running Docker containers without complex pipelines.</p>
      <pre><code>logtui docker:my-api-server</code></pre>
    </div>

    <div class="command-card">
      <h3>Structured Query Filtering</h3>
      <p>Query by log level, HTTP status codes, service names, and negations.</p>
      <pre><code>logtui demo.log --query "level:ERROR status:>=500"</code></pre>
    </div>

    <div class="command-card">
      <h3>Headless Export Pipeline</h3>
      <p>Filter logs and export matching events without opening the interactive UI.</p>
      <pre><code>logtui demo.log --headless --query "level:WARN" --export out.jsonl</code></pre>
    </div>

    <div class="command-card">
      <h3>Standard Input Support</h3>
      <p>Pipe any command output or streaming CLI tool directly into LogTUI.</p>
      <pre><code>kubectl logs -f deployment/api | logtui -</code></pre>
    </div>

    <div class="command-card">
      <h3>Live Demo Simulator</h3>
      <p>Test all capabilities instantly using the built-in generator script.</p>
      <pre><code>python generate_logs.py demo.log</code></pre>
    </div>
  </div>
</div>

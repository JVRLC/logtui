---
layout: page
title: LogTUI - The Live Log Explorer for Your Terminal
---

<script setup>
import { ref } from 'vue'

const copied = ref(false)

function copyCommand() {
  if (typeof navigator !== 'undefined' && navigator.clipboard) {
    navigator.clipboard.writeText('pipx install git+https://github.com/JVRLC/logtui.git')
    copied.value = true
    setTimeout(() => { copied.value = false }, 2200)
  }
}
</script>

<div class="hero-wrapper">
  <a href="/logtui/roadmap/" class="hero-pill">
    <span class="dot"></span>
    <span>LogTUI v0.2.0 • Query Engine, Docker & Stacktrace Aggregation</span>
    <span style="opacity: 0.6">→</span>
  </a>

  <h1 class="hero-title">
    The modern log explorer <br />
    <span class="gradient-text">built for your terminal.</span>
  </h1>

  <p class="hero-subtitle">
    Tail, filter and inspect multi-file logs, Docker containers and JSON traces with instant queries, keyboard navigation and zero configuration.
  </p>

  <div class="hero-cta">
    <a href="/logtui/getting-started/" class="btn-primary">
      <span>Get Started</span>
      <span style="font-size: 16px">→</span>
    </a>
    <a href="https://github.com/JVRLC/logtui" target="_blank" rel="noopener" class="btn-secondary">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
      </svg>
      <span>GitHub</span>
    </a>

    <div class="install-box">
      <span class="prompt">$</span>
      <span>pipx install git+https://github.com/JVRLC/logtui.git</span>
      <button class="copy-btn" @click="copyCommand">
        {{ copied ? '✓ Copied' : 'Copy' }}
      </button>
    </div>
  </div>
</div>

<!-- Interactive Terminal Sandbox (Ghostty / Warp Inspired) -->
<TerminalShowcase />

<!-- =======================================================================
     Linear / Bento Feature Grid
     ======================================================================= -->

<div class="bento-section">
  <div class="section-header">
    <div class="section-tag">Engineering Quality</div>
    <h2 class="section-title">Designed for velocity, engineered for control.</h2>
    <p class="section-desc">Everything you need to triage production incidents and understand local distributed systems.</p>
  </div>

  <div class="bento-grid">
    <!-- Card 1 (Span 2) -->
    <div class="bento-card col-span-2">
      <div>
        <span class="bento-icon">⚡</span>
        <h3>Real-Time Multi-Source Engine</h3>
        <p>Follow local log files, Docker container streams (<code>docker:api</code>), and standard input simultaneously. LogTUI runs non-blocking async workers per stream, merging independent sources into a unified, synchronized timeline.</p>
      </div>
      <div class="bento-preview">
        <code>$ logtui api.log worker.log docker:redis docker:postgres</code>
      </div>
    </div>

    <!-- Card 2 -->
    <div class="bento-card">
      <div>
        <span class="bento-icon">🔎</span>
        <h3>Embedded Query Language</h3>
        <p>Filter logs in memory with expressive syntax: <code>level:ERROR</code>, <code>status:>=500</code>, service tags, negations (<code>-service:auth</code>), and exact phrases.</p>
      </div>
      <div class="bento-preview">
        <code>/level:ERROR status:>=500</code>
      </div>
    </div>

    <!-- Card 3 -->
    <div class="bento-card">
      <div>
        <span class="bento-icon">🧵</span>
        <h3>Automatic Stacktrace Folding</h3>
        <p>Python tracebacks, Java stack exceptions, and Go panics are automatically grouped into single logical events and elevated to <code>ERROR</code> severity.</p>
      </div>
      <div class="bento-preview">
        <code>Traceback (most recent call last)...</code>
      </div>
    </div>

    <!-- Card 4 (Span 2) -->
    <div class="bento-card col-span-2">
      <div>
        <span class="bento-icon">💾</span>
        <h3>Instant Log Export &amp; Headless Pipelines</h3>
        <p>Export matching events to <code>.jsonl</code>, <code>.json</code> or <code>.csv</code> with a single keystroke (<kbd>e</kbd>) inside the TUI, or run headless in shell scripts and CI/CD workflows.</p>
      </div>
      <div class="bento-preview">
        <code>$ logtui demo.log --headless --query "status:>=500" --export report.jsonl</code>
      </div>
    </div>

    <!-- Card 5 -->
    <div class="bento-card">
      <div>
        <span class="bento-icon">🖥️</span>
        <h3>100% Local &amp; Zero Telemetry</h3>
        <p>No Elasticsearch. No Docker compose requirements. No cloud sign-up. Pure Python performance powered by Textual and Rich.</p>
      </div>
      <div class="bento-preview">
        <code>Memory: ~35MB • CPU: &lt;1% idle</code>
      </div>
    </div>
  </div>
</div>

<!-- =======================================================================
     Keyboard First Architecture (Raycast / Warp Style)
     ======================================================================= -->

<div class="keys-section">
  <div class="section-tag">Zero Mouse Reliance</div>
  <h2 style="font-size: clamp(26px, 3.5vw, 36px); font-weight: 800; color: #ffffff; margin-bottom: 12px;">
    Speed at the tip of your fingers
  </h2>
  <p style="color: #94a3b8; font-size: 16px; max-width: 580px; margin: 0 auto;">
    LogTUI is keyboard-first by default. Built for Vim enthusiasts and terminal veterans.
  </p>

  <div class="keys-grid">
    <div class="key-card">
      <kbd>j / k</kbd>
      <div class="key-info">
        <h4>Vim Navigation</h4>
        <span>Scroll through entries</span>
      </div>
    </div>

    <div class="key-card">
      <kbd>/</kbd>
      <div class="key-info">
        <h4>Structured Query</h4>
        <span>Filter by level, status, service</span>
      </div>
    </div>

    <div class="key-card">
      <kbd>Enter</kbd>
      <div class="key-info">
        <h4>Inspect JSON</h4>
        <span>Syntax-highlighted modal</span>
      </div>
    </div>

    <div class="key-card">
      <kbd>Space</kbd>
      <div class="key-info">
        <h4>Pause Stream</h4>
        <span>Buffers incoming entries</span>
      </div>
    </div>

    <div class="key-card">
      <kbd>f</kbd>
      <div class="key-info">
        <h4>Auto-Follow</h4>
        <span>Scroll with live updates</span>
      </div>
    </div>

    <div class="key-card">
      <kbd>l</kbd>
      <div class="key-info">
        <h4>Cycle Levels</h4>
        <span>ALL → INFO+ → WARN+ → ERR</span>
      </div>
    </div>

    <div class="key-card">
      <kbd>s</kbd>
      <div class="key-info">
        <h4>Filter Source</h4>
        <span>Isolate specific files</span>
      </div>
    </div>

    <div class="key-card">
      <kbd>e</kbd>
      <div class="key-info">
        <h4>Export Dialog</h4>
        <span>Save to .jsonl, .json or .csv</span>
      </div>
    </div>
  </div>
</div>

<!-- =======================================================================
     Bottom CTA Banner (Linear Style)
     ======================================================================= -->

<div class="bottom-cta">
  <h2>Upgrade your terminal workflow today.</h2>
  <p>Available on Linux, macOS, and Windows. Free, open source and fully extensible.</p>

  <div style="display: flex; justify-content: center; gap: 16px; flex-wrap: wrap;">
    <a href="/logtui/getting-started/" class="btn-primary" style="padding: 14px 32px; font-size: 16px;">
      Read the Documentation →
    </a>
    <a href="https://github.com/JVRLC/logtui" target="_blank" rel="noopener" class="btn-secondary" style="padding: 14px 28px; font-size: 16px;">
      Star on GitHub ★
    </a>
  </div>
</div>

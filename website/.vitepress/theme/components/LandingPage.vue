<script setup>
import { ref } from 'vue'

const activeTab = ref('stream')
const copied = ref(false)
const demoTab = ref('basic')

function copyCommand() {
  if (typeof navigator !== 'undefined' && navigator.clipboard) {
    navigator.clipboard.writeText('pipx install git+https://github.com/JVRLC/logtui.git')
    copied.value = true
    setTimeout(() => { copied.value = false }, 2200)
  }
}
</script>

<template>
  <div class="landing-page-root">
    <!-- Hero Section -->
    <section class="hero-wrapper">
      <a href="/logtui/roadmap/" class="hero-pill">
        <span class="dot"></span>
        <span>LogTUI v0.2.0 • Query Engine, Docker &amp; Stacktrace Aggregation</span>
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
    </section>

    <!-- Interactive Terminal Sandbox (Ghostty / Warp Inspired) -->
    <section class="terminal-showcase-container">
      <div class="terminal-window">
        <!-- Header Bar with Traffic Lights & Tab Switcher -->
        <div class="terminal-header">
          <div class="terminal-controls">
            <span class="terminal-dot dot-red"></span>
            <span class="terminal-dot dot-yellow"></span>
            <span class="terminal-dot dot-green"></span>
            <span class="terminal-header-title">LogTUI — Live log explorer</span>
          </div>

          <!-- Interactive Scenario Tabs -->
          <div class="terminal-tabs">
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'stream' }"
              @click="activeTab = 'stream'"
            >
              ● Live Stream
            </button>
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'query' }"
              @click="activeTab = 'query'"
            >
              🔍 Query Engine
            </button>
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'stacktrace' }"
              @click="activeTab = 'stacktrace'"
            >
              🧵 Stacktraces
            </button>
            <button
              class="tab-btn"
              :class="{ active: activeTab === 'inspect' }"
              @click="activeTab = 'inspect'"
            >
              ✨ Deep JSON
            </button>
          </div>

          <div class="terminal-status-info">
            <span>18:42:09 UTC</span>
          </div>
        </div>

        <!-- Terminal Main Body -->
        <div class="terminal-body">
          <!-- Sidebar -->
          <div class="terminal-sidebar">
            <div>
              <div class="sidebar-heading">SOURCES</div>
              <div class="sidebar-item" :class="{ active: activeTab !== 'query' }">
                <span>▶ demo.log</span>
                <span class="sidebar-count">1,943</span>
              </div>
              <div class="sidebar-item">
                <span>● worker.log</span>
                <span class="sidebar-count">412</span>
              </div>
              <div class="sidebar-item">
                <span>● docker:api</span>
                <span class="sidebar-count">280</span>
              </div>

              <div class="sidebar-levels">
                <div class="sidebar-heading">LEVELS</div>
                <div class="level-count-row"><span style="color: #f87171">● ERR</span> <b style="color: #f8fafc">24</b></div>
                <div class="level-count-row"><span style="color: #facc15">▲ WARN</span> <b style="color: #f8fafc">68</b></div>
                <div class="level-count-row"><span style="color: #4ade80">ℹ INFO</span> <b style="color: #f8fafc">1,420</b></div>
                <div class="level-count-row"><span style="color: #38bdf8">· DEBUG</span> <b style="color: #f8fafc">431</b></div>
                <div class="distribution-bar">
                  <div class="bar-err"></div>
                  <div class="bar-warn"></div>
                  <div class="bar-info"></div>
                  <div class="bar-dbg"></div>
                </div>
              </div>
            </div>

            <div class="sidebar-footer">
              <div>Buffer <b style="color: #f1f5f9">1,943</b> / 10,000</div>
              <div style="color: #64748b; font-size: 11px; margin-top: 2px">19% memory usage</div>
            </div>
          </div>

          <!-- Content Area -->
          <div class="terminal-content">
            <!-- Toolbar -->
            <div class="terminal-toolbar">
              <div class="toolbar-title">Live events</div>
              <div class="toolbar-tags">
                <span v-if="activeTab === 'query'" class="t-tag tag-search">🔍 "level:ERROR status:>=500"</span>
                <span v-else-if="activeTab === 'stacktrace'" class="t-tag tag-search">🔍 "Traceback"</span>
                <span class="t-tag tag-lvl">{{ activeTab === 'query' ? 'LVL: ERROR+' : 'LVL: ALL' }}</span>
                <span class="t-tag tag-src">SRC: ALL</span>
                <span class="t-tag tag-follow">FOLLOW: ON</span>
              </div>
            </div>

            <!-- Table Columns -->
            <div class="table-header">
              <span>TIME</span>
              <span>LEVEL</span>
              <span>SERVICE</span>
              <span>SOURCE</span>
              <span>MESSAGE</span>
            </div>

            <!-- Scenario 1: Standard Live Stream -->
            <div v-if="activeTab === 'stream'" class="table-rows">
              <div class="t-row">
                <span class="col-time">09:04:03</span>
                <span><span class="badge badge-info">INFO</span></span>
                <span class="col-service">billing</span>
                <span class="col-source">demo.log</span>
                <span class="col-msg">Payment confirmed: pay_77ac91 ($49.90 via Stripe)</span>
              </div>
              <div class="t-row active">
                <span class="col-time">09:06:35</span>
                <span><span class="badge badge-error">ERROR</span></span>
                <span class="col-service">database</span>
                <span class="col-source">demo.log</span>
                <span class="col-msg err-text">Database query timeout: SELECT * FROM audit_events (3004ms)</span>
              </div>
              <div class="t-row">
                <span class="col-time">09:08:47</span>
                <span><span class="badge badge-warn">WARN</span></span>
                <span class="col-service">worker</span>
                <span class="col-source">worker.log</span>
                <span class="col-msg warn-text">High memory usage: job_8842 allocated 782MB of 1024MB limit</span>
              </div>
              <div class="t-row">
                <span class="col-time">09:09:22</span>
                <span><span class="badge badge-error">ERROR</span></span>
                <span class="col-service">billing</span>
                <span class="col-source">demo.log</span>
                <span class="col-msg err-text">Payment provider unavailable: 503 upstream connection dropped</span>
              </div>
              <div class="t-row">
                <span class="col-time">09:12:15</span>
                <span><span class="badge badge-debug">DEBUG</span></span>
                <span class="col-service">database</span>
                <span class="col-source">demo.log</span>
                <span class="col-msg">Query executed in 14ms: SELECT * FROM projects WHERE owner_id = $1</span>
              </div>
              <div class="t-row">
                <span class="col-time">09:13:10</span>
                <span><span class="badge badge-info">INFO</span></span>
                <span class="col-service">api</span>
                <span class="col-source">docker:api</span>
                <span class="col-msg">GET /api/v1/health HTTP/1.1 status=200 duration=8ms user_id=usr_42</span>
              </div>
              <div class="t-row">
                <span class="col-time">09:14:35</span>
                <span><span class="badge badge-crit">CRIT</span></span>
                <span class="col-service">database</span>
                <span class="col-source">demo.log</span>
                <span class="col-msg err-text">Deadlock detected on table reservations: aborting transaction tx_819</span>
              </div>
            </div>

            <!-- Scenario 2: Structured Query Engine -->
            <div v-else-if="activeTab === 'query'" class="table-rows">
              <div class="t-row active">
                <span class="col-time">09:06:35</span>
                <span><span class="badge badge-error">ERROR</span></span>
                <span class="col-service">api</span>
                <span class="col-source">docker:api</span>
                <span class="col-msg err-text">GET /api/audit failed status=504 duration_ms=3021 (DatabaseTimeout)</span>
              </div>
              <div class="t-row">
                <span class="col-time">09:09:22</span>
                <span><span class="badge badge-error">ERROR</span></span>
                <span class="col-service">billing</span>
                <span class="col-source">demo.log</span>
                <span class="col-msg err-text">POST /api/v1/charge failed status=503 error="Service Unavailable"</span>
              </div>
              <div class="t-row">
                <span class="col-time">09:16:40</span>
                <span><span class="badge badge-error">ERROR</span></span>
                <span class="col-service">auth</span>
                <span class="col-source">docker:api</span>
                <span class="col-msg err-text">POST /oauth/token status=500 duration_ms=1890 internal_error=true</span>
              </div>
            </div>

            <!-- Scenario 3: Stacktrace Aggregation -->
            <div v-else-if="activeTab === 'stacktrace'" class="table-rows" style="padding: 14px 18px;">
              <div style="background: rgba(239, 68, 68, 0.08); border-left: 3px solid #ef4444; border-radius: 6px; padding: 14px; font-family: var(--vp-font-family-mono);">
                <div style="display: flex; gap: 12px; align-items: center; margin-bottom: 8px;">
                  <span class="badge badge-error">ERROR</span>
                  <span class="col-service">worker</span>
                  <span class="col-source">worker.log</span>
                  <span class="col-time">10:00:06</span>
                </div>
                <div style="color: #fca5a5; font-weight: 700; margin-bottom: 8px">
                  Unhandled exception during background job (4 lines folded into 1 event)
                </div>
                <pre style="margin: 0; background: #020617; padding: 12px; border-radius: 6px; color: #94a3b8; font-size: 12px; line-height: 1.5; overflow-x: auto;">Traceback (most recent call last):
  File "app/worker.py", line 88, in process_job
    response = requests.post(webhook_url, json=payload, timeout=5)
ConnectionError: Failed to establish connection to upstream webhook:5000</pre>
              </div>
            </div>

            <!-- Scenario 4: Deep JSON Inspection -->
            <div v-else-if="activeTab === 'inspect'" class="table-rows" style="padding: 14px 18px;">
              <div style="background: #0d1322; border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 8px; padding: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                  <span style="color: #38bdf8; font-weight: 700;">🔍 Log Entry Detail &amp; Structured Fields</span>
                  <span style="color: #64748b; font-size: 11px;">Press [c] to copy raw JSON</span>
                </div>
                <pre style="margin: 0; background: #020617; padding: 14px; border-radius: 6px; color: #38bdf8; font-size: 12.5px; line-height: 1.5; overflow-x: auto;">{
  <span style="color: #a78bfa">"timestamp"</span>: <span style="color: #4ade80">"2026-10-18T09:06:35.021Z"</span>,
  <span style="color: #a78bfa">"level"</span>: <span style="color: #f87171">"ERROR"</span>,
  <span style="color: #a78bfa">"service"</span>: <span style="color: #38bdf8">"database"</span>,
  <span style="color: #a78bfa">"message"</span>: <span style="color: #f1f5f9">"Database query timeout"</span>,
  <span style="color: #a78bfa">"request_id"</span>: <span style="color: #facc15">"req_a1b322"</span>,
  <span style="color: #a78bfa">"status"</span>: <span style="color: #f87171">504</span>,
  <span style="color: #a78bfa">"duration_ms"</span>: <span style="color: #facc15">3004</span>,
  <span style="color: #a78bfa">"retryable"</span>: <span style="color: #f87171">true</span>
}</pre>
              </div>
            </div>

            <!-- Status Bar -->
            <div class="terminal-status-bar">
              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="color: #4ade80; font-weight: 700;">● LIVE</span>
                <span style="color: #94a3b8">Following files</span>
              </div>
              <div style="color: #38bdf8; font-weight: 700;">
                {{ activeTab === 'query' ? '3 of 1,943 events' : '1,943 events' }}
              </div>
            </div>

            <!-- Footer Keybinds -->
            <div class="terminal-footer-keys">
              <div><span class="key-pill">q</span>Quit</div>
              <div><span class="key-pill">space</span>Pause</div>
              <div><span class="key-pill">/</span>Query</div>
              <div><span class="key-pill">l</span>Level</div>
              <div><span class="key-pill">s</span>Source</div>
              <div><span class="key-pill">e</span>Export</div>
              <div><span class="key-pill">enter</span>Details</div>
              <div><span class="key-pill">?</span>Help</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Linear / Bento Feature Grid -->
    <section class="bento-section">
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
    </section>

    <!-- Keyboard First Architecture (Raycast / Warp Style) -->
    <section class="keys-section">
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
    </section>

    <!-- Bottom CTA Banner (Linear Style) -->
    <section class="bottom-cta">
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
    </section>
  </div>
</template>

<style scoped>
.terminal-header-title {
  margin-left: 8px;
  font-weight: 700;
  color: #94a3b8;
  font-size: 13px;
}
</style>

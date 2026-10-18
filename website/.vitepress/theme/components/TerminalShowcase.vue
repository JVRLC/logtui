<script setup>
import { ref } from 'vue'

const activeTab = ref('stream')
</script>

<template>
  <div class="terminal-showcase-container">
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
          <div v-else-if="activeTab === 'stacktrace'" class="table-rows" style="padding: 12px 18px;">
            <div style="background: rgba(239, 68, 68, 0.08); border-left: 3px solid #ef4444; border-radius: 6px; padding: 14px; font-family: var(--vp-font-family-mono);">
              <div style="display: flex; gap: 12px; align-items: center; margin-bottom: 8px;">
                <span class="badge badge-error">ERROR</span>
                <span style="color: #38bdf8; font-weight: 700">worker</span>
                <span style="color: #a78bfa">worker.log</span>
                <span style="color: #64748b">10:00:06</span>
              </div>
              <div style="color: #fca5a5; font-weight: 700; margin-bottom: 8px">
                Unhandled exception occurred during background processing (4 lines aggregated)
              </div>
              <pre style="margin: 0; background: #020617; padding: 12px; border-radius: 6px; color: #94a3b8; font-size: 12px; line-height: 1.5; overflow-x: auto;">Traceback (most recent call last):
  File "app/worker.py", line 88, in process_job
    response = requests.post(webhook_url, json=payload, timeout=5)
ConnectionError: Failed to establish connection to upstream webhook:5000</pre>
            </div>
          </div>

          <!-- Scenario 4: Deep JSON Inspection -->
          <div v-else-if="activeTab === 'inspect'" class="table-rows" style="padding: 12px 18px;">
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


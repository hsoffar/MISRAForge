import { useEffect, useMemo, useState } from 'react'
import './App.css'

type SummaryPayload = {
  summary?: {
    by_status?: Record<string, number>
  }
  by_file: Record<string, number>
  by_rule: Record<string, number>
  deviation_by_rule: Record<string, number>
  files: string[]
}

type Finding = {
  rule_id: string
  status: string
  severity: string
  message: string
  recommendation?: string
  fingerprint?: string
  location: { path: string; line: number; column: number }
}

type RuleInfo = {
  rule_id: string
  title: string
  category: string
  level: string
  severity: string
  languages: string[]
  rationale_summary: string
  detected_count: number
  tested: boolean
  implemented: boolean
  content_summary: string
  content_full_text: string
  content_notes: string
  content_source: string
  content_license: string
}

type RulesPayload = { rules: RuleInfo[] }

type FilesPayload = {
  root: string
  file_count: number
  folder_count: number
  tree: TreeNode
}

type TreeNode = { name: string; files?: string[]; folders?: TreeNode[] }

type TabId = 'overview' | 'findings' | 'explorer' | 'rules' | 'deviations'

const navItems: Array<{ id: TabId; label: string }> = [
  { id: 'overview', label: 'Overview' },
  { id: 'findings', label: 'Findings' },
  { id: 'explorer', label: 'Explorer' },
  { id: 'rules', label: 'Rules' },
  { id: 'deviations', label: 'Deviations' },
]

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(path)
  if (!res.ok) throw new Error(`${path} => ${res.status}`)
  return (await res.json()) as T
}

function App() {
  const [activeTab, setActiveTab] = useState<TabId>('findings')
  const [targetType, setTargetType] = useState<'repo' | 'file'>('repo')
  const [targetPath, setTargetPath] = useState('samples/simple_repo')
  const [outputDir, setOutputDir] = useState('out')
  const [deviationFile, setDeviationFile] = useState('samples/deviations.yaml')
  const [runStatus, setRunStatus] = useState('')
  const [runState, setRunState] = useState<'idle' | 'running' | 'success' | 'error'>('idle')
  const [runProgress, setRunProgress] = useState(0)

  const [summary, setSummary] = useState<SummaryPayload>({ by_file: {}, by_rule: {}, deviation_by_rule: {}, files: [] })
  const [rules, setRules] = useState<RulesPayload>({ rules: [] })
  const [files, setFiles] = useState<FilesPayload | null>(null)
  const [latestFindings, setLatestFindings] = useState<Finding[]>([])

  const [groupBy, setGroupBy] = useState<'flat' | 'file' | 'rule' | 'status'>('file')
  const [severity, setSeverity] = useState('')
  const [status, setStatus] = useState('')
  const [ruleIdFilter, setRuleIdFilter] = useState('')
  const [search, setSearch] = useState('')
  const [selectedFile, setSelectedFile] = useState('')
  const [findingsGroups, setFindingsGroups] = useState<Record<string, Finding[]>>({})
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null)

  const [hoverRule, setHoverRule] = useState<RuleInfo | null>(null)
  const [hoverPos, setHoverPos] = useState<{ x: number; y: number } | null>(null)

  const kpiFindings = useMemo(() => Object.values(summary.by_rule).reduce((acc, n) => acc + Number(n || 0), 0), [summary.by_rule])
  const kpiRulesHit = useMemo(() => Object.keys(summary.by_rule).length, [summary.by_rule])
  const kpiDeviations = useMemo(
    () => Object.values(summary.deviation_by_rule).reduce((acc, n) => acc + Number(n || 0), 0),
    [summary.deviation_by_rule]
  )
  const statusCounts = useMemo(() => summary.summary?.by_status ?? {}, [summary.summary])
  const severityCounts = useMemo(() => {
    const counts: Record<string, number> = {}
    for (const item of latestFindings) {
      const key = (item.severity || 'unknown').toLowerCase()
      counts[key] = (counts[key] ?? 0) + 1
    }
    return counts
  }, [latestFindings])

  async function refreshSummary() {
    setSummary(await apiGet<SummaryPayload>('/api/summary'))
  }

  async function refreshRules() {
    setRules(await apiGet<RulesPayload>('/api/rules'))
  }

  async function refreshLatestFindings() {
    const payload = await apiGet<{ findings?: Finding[] }>('/api/scan/latest')
    setLatestFindings(payload.findings ?? [])
  }

  async function refreshFiles() {
    const root = targetPath.trim() || '.'
    setFiles(await apiGet<FilesPayload>(`/api/files?root=${encodeURIComponent(root)}`))
  }

  async function refreshFindings() {
    const query = new URLSearchParams({
      group_by: groupBy,
      q: search,
      severity,
      status,
      rule_id: ruleIdFilter,
      file_path: selectedFile,
    })
    const payload = await apiGet<{ groups: Record<string, Finding[]> }>(`/api/findings?${query.toString()}`)
    setFindingsGroups(payload.groups ?? {})

    const first = Object.values(payload.groups ?? {}).flat()[0]
    setSelectedFinding(first ?? null)
  }

  async function refreshAll() {
    await Promise.all([refreshSummary(), refreshRules(), refreshFiles(), refreshFindings(), refreshLatestFindings()])
  }

  useEffect(() => {
    refreshAll().catch((err) => setRunStatus(String(err)))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function runScan() {
    setRunState('running')
    setRunProgress(8)
    setRunStatus('Running scan...')
    try {
      const res = await fetch('/api/scan/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target: targetPath,
          target_type: targetType,
          output_dir: outputDir,
          deviation_file: deviationFile || null,
          formats: ['json', 'html', 'csv'],
        }),
      })
      setRunProgress(64)
      const payload = await res.json()
      if (!res.ok) throw new Error(payload.detail || 'scan failed')
      setRunStatus('Refreshing visualizations...')
      await refreshAll()
      setRunProgress(100)
      setRunState('success')
      setRunStatus('Run complete')
      window.setTimeout(() => {
        setRunState('idle')
        setRunProgress(0)
      }, 1500)
    } catch (err) {
      setRunState('error')
      setRunProgress(100)
      setRunStatus(String(err))
      throw err
    }
  }

  function onFileSelect(path: string) {
    setSelectedFile(path)
    setTargetType('file')
    setTargetPath(path)
    setActiveTab('findings')
  }

  function renderTree(node?: TreeNode) {
    if (!node) return <div className="empty">No source files found</div>
    return (
      <div className="tree-node">
        {(node.folders ?? []).map((folder) => (
          <details key={`${node.name}-${folder.name}`}>
            <summary>{folder.name}</summary>
            {renderTree(folder)}
          </details>
        ))}
        {(node.files ?? []).map((filePath) => (
          <button className="file-link" key={filePath} onClick={() => onFileSelect(filePath)}>
            {filePath}
          </button>
        ))}
      </div>
    )
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="logo">MISRAForge</div>
        <div className="logo-sub">Static Analysis Console</div>
        <nav className="nav">
          {navItems.map((item) => (
            <button
              key={item.id}
              className={activeTab === item.id ? 'nav-btn active' : 'nav-btn'}
              onClick={() => setActiveTab(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </aside>

      <main className="main">
        <header className="topbar">
          <div className="scan-controls">
            <select value={targetType} onChange={(e) => setTargetType(e.target.value as 'repo' | 'file')}>
              <option value="repo">Repository</option>
              <option value="file">Single file</option>
            </select>
            <input value={targetPath} onChange={(e) => setTargetPath(e.target.value)} placeholder="Target path" />
            <input value={outputDir} onChange={(e) => setOutputDir(e.target.value)} placeholder="Output dir" />
            <input value={deviationFile} onChange={(e) => setDeviationFile(e.target.value)} placeholder="Deviation file" />
          </div>
          <div className="actions">
            <button
              className="primary"
              disabled={runState === 'running'}
              onClick={() => {
                runScan().catch((err) => setRunStatus(String(err)))
              }}
            >
              Run Scan
            </button>
            <button
              disabled={runState === 'running'}
              onClick={() => {
                refreshAll().catch((err) => setRunStatus(String(err)))
              }}
            >
              Refresh
            </button>
            <button
              disabled={runState === 'running'}
              onClick={() => {
                refreshFiles().catch((err) => setRunStatus(String(err)))
              }}
            >
              Browse
            </button>
          </div>
        </header>

        <div className={`status-row ${runState}`}>
          <div className="status-text">{runStatus || 'Ready'}</div>
          <div className="progress-wrap">
            <div
              className={runState === 'running' ? 'progress-bar running' : 'progress-bar'}
              style={{ width: `${runProgress}%` }}
            />
          </div>
        </div>

        <section className="kpis">
          <article className="kpi"><div className="kpi-k">Files</div><div className="kpi-v">{summary.files.length}</div></article>
          <article className="kpi"><div className="kpi-k">Findings</div><div className="kpi-v">{kpiFindings}</div></article>
          <article className="kpi"><div className="kpi-k">Rules Hit</div><div className="kpi-v">{kpiRulesHit}</div></article>
          <article className="kpi"><div className="kpi-k">Deviations</div><div className="kpi-v">{kpiDeviations}</div></article>
        </section>

        {activeTab === 'overview' && (
          <section className="panel-grid two">
            <article className="panel">
              <h3>Top Files by Findings</h3>
              <table>
                <thead><tr><th>File</th><th>Issues</th></tr></thead>
                <tbody>
                  {Object.entries(summary.by_file).slice(0, 20).map(([p, c]) => (
                    <tr key={p}><td>{p}</td><td>{c}</td></tr>
                  ))}
                </tbody>
              </table>
            </article>
            <article className="panel">
              <h3>Findings by Rule</h3>
              <table>
                <thead><tr><th>Rule</th><th>Issues</th></tr></thead>
                <tbody>
                  {Object.entries(summary.by_rule).map(([r, c]) => (
                    <tr key={r}><td>{r}</td><td>{c}</td></tr>
                  ))}
                </tbody>
              </table>
            </article>
            <article className="panel">
              <h3>Status Distribution</h3>
              <div className="mini-bars">
                {Object.entries(statusCounts).map(([name, count]) => (
                  <div key={name} className="mini-row">
                    <div className="mini-label">{name}</div>
                    <div className="mini-track">
                      <div
                        className="mini-fill status"
                        style={{ width: `${kpiFindings > 0 ? (Number(count) / kpiFindings) * 100 : 0}%` }}
                      />
                    </div>
                    <div className="mini-value">{count}</div>
                  </div>
                ))}
                {Object.keys(statusCounts).length === 0 && <div className="empty">No status data yet.</div>}
              </div>
            </article>
            <article className="panel">
              <h3>Severity Distribution</h3>
              <div className="mini-bars">
                {Object.entries(severityCounts).map(([name, count]) => (
                  <div key={name} className="mini-row">
                    <div className="mini-label">{name}</div>
                    <div className="mini-track">
                      <div
                        className={`mini-fill sev-${name}`}
                        style={{ width: `${kpiFindings > 0 ? (Number(count) / kpiFindings) * 100 : 0}%` }}
                      />
                    </div>
                    <div className="mini-value">{count}</div>
                  </div>
                ))}
                {Object.keys(severityCounts).length === 0 && <div className="empty">No severity data yet.</div>}
              </div>
            </article>
          </section>
        )}

        {activeTab === 'findings' && (
          <section className="panel-grid findings-layout">
            <article className="panel filters-panel">
              <h3>Filters</h3>
              <label>Group</label>
              <select value={groupBy} onChange={(e) => setGroupBy(e.target.value as typeof groupBy)}>
                <option value="file">File</option>
                <option value="rule">Rule</option>
                <option value="status">Status</option>
                <option value="flat">Flat</option>
              </select>
              <label>Severity</label>
              <select value={severity} onChange={(e) => setSeverity(e.target.value)}>
                <option value="">All</option><option value="info">Info</option><option value="low">Low</option>
                <option value="medium">Medium</option><option value="high">High</option>
              </select>
              <label>Status</label>
              <select value={status} onChange={(e) => setStatus(e.target.value)}>
                <option value="">All</option><option value="confirmed">Confirmed</option><option value="possible">Possible</option>
                <option value="manual_review">Manual review</option><option value="suppressed">Suppressed</option>
                <option value="baseline">Baseline</option><option value="deviation">Deviation</option>
              </select>
              <label>Rule ID</label>
              <input value={ruleIdFilter} onChange={(e) => setRuleIdFilter(e.target.value)} placeholder="MC3R-..." />
              <label>Text</label>
              <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="search findings" />
              <label>Selected file</label>
              <div className="selected-file">{selectedFile || 'none'}</div>
              <button
                className="primary"
                onClick={() => {
                  refreshFindings().catch((err) => setRunStatus(String(err)))
                }}
              >
                Apply filters
              </button>
              <button
                onClick={() => {
                  setSelectedFile('')
                  refreshFindings().catch((err) => setRunStatus(String(err)))
                }}
              >
                Clear file filter
              </button>
            </article>

            <article className="panel list-panel">
              <h3>Issue Groups</h3>
              <div className="groups-scroll">
                {Object.entries(findingsGroups).map(([group, items]) => (
                  <div key={group} className="group-block">
                    <div className="group-title">{group} ({items.length})</div>
                    <table>
                      <thead><tr><th>Rule</th><th>Status</th><th>Severity</th><th>Location</th><th>Message</th></tr></thead>
                      <tbody>
                        {items.map((f, idx) => (
                          <tr key={`${group}-${idx}`} onClick={() => setSelectedFinding(f)}>
                            <td>{f.rule_id}</td>
                            <td>{f.status}</td>
                            <td>{f.severity}</td>
                            <td>{f.location.path}:{f.location.line}:{f.location.column}</td>
                            <td>{f.message}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ))}
              </div>
            </article>

            <article className="panel detail-panel">
              <h3>Issue Detail</h3>
              {!selectedFinding && <div className="empty">Select an issue row</div>}
              {selectedFinding && (
                <div className="detail-body">
                  <div><strong>Rule:</strong> {selectedFinding.rule_id}</div>
                  <div><strong>Status:</strong> {selectedFinding.status}</div>
                  <div><strong>Severity:</strong> {selectedFinding.severity}</div>
                  <div><strong>Location:</strong> {selectedFinding.location.path}:{selectedFinding.location.line}:{selectedFinding.location.column}</div>
                  <div><strong>Message:</strong> {selectedFinding.message}</div>
                  <div><strong>Recommendation:</strong> {selectedFinding.recommendation || '-'}</div>
                  <div><strong>Fingerprint:</strong> {selectedFinding.fingerprint || '-'}</div>
                </div>
              )}
            </article>
          </section>
        )}

        {activeTab === 'explorer' && (
          <section className="panel-grid two">
            <article className="panel">
              <h3>Project Tree</h3>
              <div className="meta">root={files?.root || '-'} folders={files?.folder_count || 0} files={files?.file_count || 0}</div>
              <div className="tree-scroll">{renderTree(files?.tree)}</div>
            </article>
            <article className="panel">
              <h3>Files With Findings</h3>
              <table>
                <thead><tr><th>File</th><th>Issues</th><th></th></tr></thead>
                <tbody>
                  {Object.entries(summary.by_file).map(([path, count]) => (
                    <tr key={path}>
                      <td>{path}</td>
                      <td>{count}</td>
                      <td><button onClick={() => onFileSelect(path)}>Inspect</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </article>
          </section>
        )}

        {activeTab === 'rules' && (
          <section className="panel-grid two">
            <article className="panel">
              <h3>Rules Catalog</h3>
              <table>
                <thead><tr><th>Rule</th><th>Category</th><th>Detected</th><th>Tested</th></tr></thead>
                <tbody>
                  {rules.rules.map((r) => (
                    <tr
                      key={r.rule_id}
                      onMouseEnter={(ev) => {
                        setHoverRule(r)
                        setHoverPos({ x: ev.clientX + 12, y: ev.clientY + 12 })
                      }}
                      onMouseMove={(ev) => setHoverPos({ x: ev.clientX + 12, y: ev.clientY + 12 })}
                      onMouseLeave={() => setHoverRule(null)}
                    >
                      <td>{r.rule_id}</td><td>{r.category}</td><td>{r.detected_count}</td><td>{r.tested ? 'yes' : 'no'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </article>
            <article className="panel">
              <h3>Rule Notes</h3>
              <p className="empty">Hover a rule row to view details in a flyover.</p>
            </article>
          </section>
        )}

        {activeTab === 'deviations' && (
          <section className="panel-grid one">
            <article className="panel">
              <h3>Deviation by Rule</h3>
              <table>
                <thead><tr><th>Rule</th><th>Count</th></tr></thead>
                <tbody>
                  {Object.entries(summary.deviation_by_rule).map(([r, c]) => (
                    <tr key={r}><td>{r}</td><td>{c}</td></tr>
                  ))}
                </tbody>
              </table>
            </article>
          </section>
        )}
      </main>

      {hoverRule && hoverPos && (
        <div className="flyover" style={{ left: hoverPos.x, top: hoverPos.y }}>
          <div className="fly-title">{hoverRule.rule_id} - {hoverRule.title}</div>
          <div className="fly-meta">{hoverRule.category} | {hoverRule.level} | {hoverRule.severity}</div>
          <div className="fly-meta">source: {hoverRule.content_source || 'local metadata'}</div>
          <div className="fly-body">{hoverRule.content_summary || hoverRule.rationale_summary}</div>
          <div className="fly-body">{hoverRule.content_full_text || hoverRule.content_notes || 'No local full text in content pack.'}</div>
        </div>
      )}
    </div>
  )
}

export default App

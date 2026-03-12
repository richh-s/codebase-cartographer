/* ──────────────────────────────────────────────────────────────────────────
   Codebase Cartographer — Frontend Application
   ────────────────────────────────────────────────────────────────────────── */

const API = ''; // Relative, same origin
let REPO_PATH = '';

// ── State ─────────────────────────────────────────────────────────────────
const state = {
    moduleGraph: null,
    lineageGraph: null,
    status: null,
};

// ── DOM helpers ───────────────────────────────────────────────────────────
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => [...document.querySelectorAll(sel)];

function setLoading(on) {
    let overlay = document.getElementById('loadingOverlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.innerHTML = `<div class="loading-spinner"></div><span>Loading…</span>`;
        document.body.appendChild(overlay);
    }
    overlay.classList.toggle('show', on);
}

function formatTime(iso) {
    if (!iso) return '—';
    try { return new Date(iso).toLocaleString(); } catch { return iso; }
}

function shortenPath(path) {
    if (!path) return '—';
    const parts = path.split('/');
    return parts.length > 3 ? '…/' + parts.slice(-2).join('/') : path;
}

// ── API fetch ─────────────────────────────────────────────────────────────
async function apiFetch(endpoint, options = {}) {
    const sep = endpoint.includes('?') ? '&' : '?';
    const url = REPO_PATH ? `${API}${endpoint}${sep}repo_path=${encodeURIComponent(REPO_PATH)}` : `${API}${endpoint}`;
    try {
        const r = await fetch(url, options);
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
    } catch (e) {
        console.warn(`[API] ${endpoint} failed:`, e.message);
        return null;
    }
}

// ── Tab navigation ────────────────────────────────────────────────────────
function switchTab(tab) {
    $$('.nav-item').forEach(el => el.classList.toggle('active', el.dataset.tab === tab));
    $$('.tab').forEach(el => el.classList.toggle('active', el.id === `tab-${tab}`));
    $('#pageTitle').textContent = {
        'dashboard': 'Dashboard',
        'module-graph': 'Module Graph',
        'lineage-graph': 'Lineage Graph',
        'navigator': 'Navigator Agent',
        'artifacts': 'Artifacts',
        'trace': 'Trace Log',
    }[tab] || tab;

    // Lazy-load tab data
    if (tab === 'module-graph' && !state.moduleGraph) loadModuleGraph();
    if (tab === 'lineage-graph' && !state.lineageGraph) loadLineageGraph();
    if (tab === 'artifacts') loadArtifact($('.artifact-tab.active')?.dataset.artifact || 'codebase');
    if (tab === 'trace') loadTrace();
}

$$('.nav-item').forEach(el => el.addEventListener('click', () => switchTab(el.dataset.tab)));

// ── Repo selector ──────────────────────────────────────────────────────────
document.getElementById('setRepoBtn').addEventListener('click', () => {
    REPO_PATH = document.getElementById('repoPathInput').value.trim();
    state.moduleGraph = null;
    state.lineageGraph = null;
    initDashboard();
});
document.getElementById('repoPathInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') document.getElementById('setRepoBtn').click();
});

// ── Dashboard ─────────────────────────────────────────────────────────────
async function initDashboard() {
    setLoading(true);
    const [statusData, statsData, mgData] = await Promise.all([
        apiFetch('/api/status'),
        apiFetch('/api/stats'),
        apiFetch('/api/module-graph'),
    ]);
    setLoading(false);

    if (statusData) {
        state.status = statusData;
        const dot = $('#statusDot');
        dot.className = `status-dot ${statusData.has_analysis ? 'dot-ready' : 'dot-idle'}`;

        if (statusData.git_commit && statusData.git_commit !== 'N/A') {
            const cb = $('#commitBadge');
            cb.textContent = `git: ${statusData.git_commit.substring(0, 8)}`;
            cb.classList.remove('hidden');
        }
        if (statusData.timestamp && statusData.timestamp !== 'N/A') {
            const tb = $('#timestampBadge');
            tb.textContent = formatTime(statusData.timestamp);
            tb.classList.remove('hidden');
        }
    }

    if (statsData) {
        $('#statsModules').textContent = statsData.modules ?? '—';
        $('#statsEdges').textContent = statsData.edges ?? '—';
        $('#statsHubs').textContent = statsData.hubs ?? '—';
        $('#statsDead').textContent = statsData.dead_code ?? '—';
        $('#statsData').textContent = statsData.data_nodes ?? '—';
        $('#statsLineage').textContent = statsData.lineage_edges ?? '—';
    }

    if (mgData && mgData.nodes) {
        state.moduleGraph = mgData;
        renderHubs(mgData.nodes);
        renderVelocity(mgData.nodes);
        renderDomains(mgData.nodes);
        renderDebt(mgData.nodes);
    }
}

function renderHubs(nodes) {
    const hubs = nodes.filter(n => n.is_architectural_hub)
        .sort((a, b) => (b.pagerank_score || 0) - (a.pagerank_score || 0))
        .slice(0, 8);
    const el = $('#hubsList');
    el.innerHTML = hubs.length ? hubs.map(n => `
    <div class="module-row">
      <span class="module-path">${shortenPath(n.path)}</span>
      <span class="module-badge badge-hub">hub</span>
      <span style="font-size:10px;color:var(--text-muted)">${(n.pagerank_score || 0).toFixed(3)}</span>
    </div>`).join('') : '<p class="placeholder-text">No hubs detected</p>';
}

function renderVelocity(nodes) {
    const high = nodes.filter(n => n.is_high_velocity || n.change_velocity_30d > 0)
        .sort((a, b) => (b.change_velocity_30d || 0) - (a.change_velocity_30d || 0))
        .slice(0, 8);
    const el = $('#velocityList');
    el.innerHTML = high.length ? high.map(n => `
    <div class="module-row">
      <span class="module-path">${shortenPath(n.path)}</span>
      <span class="module-badge badge-vel">${(n.change_velocity_30d || 0).toFixed(1)} chg/mo</span>
    </div>`).join('') : '<p class="placeholder-text">No velocity data</p>';
}

function renderDomains(nodes) {
    const domainMap = {};
    nodes.forEach(n => {
        if (n.domain_cluster) domainMap[n.domain_cluster] = (domainMap[n.domain_cluster] || 0) + 1;
    });
    const el = $('#domainsList');
    const chips = Object.entries(domainMap).map(([d, cnt]) =>
        `<div class="domain-chip">${d} <span class="domain-count">${cnt}</span></div>`
    ).join('');
    el.innerHTML = chips || '<p class="placeholder-text">Run with --llm for domain clustering</p>';
}

function renderDebt(nodes) {
    const debt = nodes.filter(n => n.is_dead_code_candidate || n.documentation_drift).slice(0, 8);
    const el = $('#debtList');
    el.innerHTML = debt.length ? debt.map(n => `
    <div class="module-row">
      <span class="module-path">${shortenPath(n.path)}</span>
      ${n.is_dead_code_candidate ? '<span class="module-badge badge-dead">dead code</span>' : ''}
      ${n.documentation_drift ? '<span class="module-badge badge-vel">doc drift</span>' : ''}
    </div>`).join('') : '<p class="placeholder-text">No debt detected 🎉</p>';
}

// ── Run Analysis button ───────────────────────────────────────────────────
document.getElementById('analyzeBtn').addEventListener('click', async () => {
    const btn = document.getElementById('analyzeBtn');
    const status = document.getElementById('analyzeStatus');
    btn.disabled = true;
    status.textContent = '⚡ Analysis running…';
    status.classList.remove('hidden');

    const result = await fetch(`${API}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_path: REPO_PATH || '.', llm_enabled: false }),
    }).then(r => r.json()).catch(() => null);

    if (result?.status === 'started') {
        status.textContent = '✅ Analysis started in background…';
        setTimeout(() => {
            status.textContent = '🔄 Refreshing results…';
            state.moduleGraph = null;
            state.lineageGraph = null;
            initDashboard();
            setTimeout(() => {
                btn.disabled = false;
                status.classList.add('hidden');
            }, 3000);
        }, 5000);
    } else {
        status.textContent = '❌ Could not start analysis.';
        btn.disabled = false;
    }
});

// ── D3 Force Graph utility ────────────────────────────────────────────────
function createForceGraph(svgId, containerId, nodes, links, nodeColor, nodeRadius, labelFn, tooltipFn, clickFn) {
    const container = document.getElementById(containerId);
    const svg = d3.select(`#${svgId}`);
    svg.selectAll('*').remove();

    const W = container.clientWidth;
    const H = container.clientHeight;
    svg.attr('viewBox', `0 0 ${W} ${H}`);

    const g = svg.append('g');

    // Zoom + pan
    svg.call(d3.zoom().scaleExtent([0.1, 5]).on('zoom', e => g.attr('transform', e.transform)));

    // Tooltip div
    const tooltip = document.getElementById(`${svgId.replace('Svg', 'Tooltip')}`);

    // Arrow marker for directed edges
    svg.append('defs').append('marker')
        .attr('id', 'arrow')
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 18).attr('refY', 0)
        .attr('markerWidth', 6).attr('markerHeight', 6)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', '#2a3c60');

    const sim = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.id).distance(80).strength(0.3))
        .force('charge', d3.forceManyBody().strength(-200))
        .force('center', d3.forceCenter(W / 2, H / 2))
        .force('collision', d3.forceCollide().radius(d => nodeRadius(d) + 4));

    const link = g.append('g')
        .selectAll('line')
        .data(links)
        .join('line')
        .attr('stroke-width', 1)
        .attr('stroke', '#2a3c60')
        .attr('stroke-opacity', 0.6)
        .attr('marker-end', 'url(#arrow)');

    const node = g.append('g')
        .selectAll('circle')
        .data(nodes)
        .join('circle')
        .attr('r', d => nodeRadius(d))
        .attr('fill', d => nodeColor(d))
        .attr('fill-opacity', 0.85)
        .attr('stroke', '#0a0e17')
        .attr('stroke-width', 1.5)
        .style('cursor', 'pointer')
        .call(d3.drag()
            .on('start', (e, d) => { if (!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
            .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y; })
            .on('end', (e, d) => { if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null; })
        )
        .on('mouseover', (e, d) => {
            tooltip.innerHTML = tooltipFn(d);
            tooltip.classList.remove('hidden');
        })
        .on('mousemove', (e) => {
            tooltip.style.left = (e.offsetX + 14) + 'px';
            tooltip.style.top = (e.offsetY - 10) + 'px';
        })
        .on('mouseout', () => tooltip.classList.add('hidden'))
        .on('click', (e, d) => { e.stopPropagation(); if (clickFn) clickFn(d); });

    const label = g.append('g')
        .selectAll('text')
        .data(nodes)
        .join('text')
        .text(d => labelFn(d))
        .attr('font-size', 9)
        .attr('fill', '#7b93c2')
        .attr('pointer-events', 'none')
        .attr('dy', 4)
        .attr('text-anchor', 'middle');

    sim.on('tick', () => {
        link
            .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
        node.attr('cx', d => d.x).attr('cy', d => d.y);
        label.attr('x', d => d.x).attr('y', d => d.y + nodeRadius(d) + 10);
    });

    return { sim, node, link, label, g };
}

// ── Module Graph ──────────────────────────────────────────────────────────
async function loadModuleGraph() {
    if (!state.moduleGraph) {
        setLoading(true);
        state.moduleGraph = await apiFetch('/api/module-graph');
        setLoading(false);
    }
    if (!state.moduleGraph) return;
    renderModuleGraph(state.moduleGraph);
}

function renderModuleGraph(graph) {
    const hideInfo = document.getElementById('filterHideInfo').checked;
    const hubsOnly = document.getElementById('filterHubsOnly').checked;
    const search = document.getElementById('graphSearch').value.toLowerCase();

    let nodes = graph.nodes?.map(n => ({ ...n, id: n.identity })) || [];
    let edges = graph.edges?.map(e => ({ source: e.source, target: e.target })) || [];

    if (hideInfo) nodes = nodes.filter(n => !n.is_informational);
    if (hubsOnly) nodes = nodes.filter(n => n.is_architectural_hub);
    if (search) nodes = nodes.filter(n => (n.path || '').toLowerCase().includes(search) || (n.identity || '').includes(search));

    const nodeIds = new Set(nodes.map(n => n.id));
    edges = edges.filter(e => nodeIds.has(e.source) && nodeIds.has(e.target));

    document.getElementById('graphNodeCount').textContent = `${nodes.length} nodes`;

    const nodeColor = d => {
        if (d.is_architectural_hub) return '#a855f7';
        if (d.is_dead_code_candidate) return '#f43f5e';
        if (d.is_informational) return '#465a80';
        return '#00e5ff';
    };
    const nodeRadius = d => {
        if (d.is_architectural_hub) return 9;
        if (d.is_high_velocity) return 7;
        return 5;
    };
    const labelFn = d => {
        const parts = (d.path || '').split('/');
        return parts[parts.length - 1] || d.identity;
    };
    const tooltipFn = d => `
    <strong>${d.identity}</strong><br/>
    <span style="color:#7b93c2">${d.path}</span><br/>
    Layer: ${d.architecture_layer}<br/>
    Complexity: ${(d.complexity_score || 0).toFixed(1)} | PageRank: ${(d.pagerank_score || 0).toFixed(3)}
    ${d.purpose_statement ? `<br/><em style="color:#7b93c2;font-size:11px">${d.purpose_statement.substring(0, 80)}…</em>` : ''}
  `;
    const clickFn = d => showModuleDetail(d);

    createForceGraph('moduleGraphSvg', 'moduleGraphContainer', nodes, edges, nodeColor, nodeRadius, labelFn, tooltipFn, clickFn);
}

function showModuleDetail(d) {
    const panel = document.getElementById('moduleNodeDetail');
    panel.classList.remove('hidden');

    const funcs = (d.functions || []).map(f => `<code style="display:block;margin-bottom:3px;font-size:11px;color:var(--cyan)">${f.qualified_name}</code>`).slice(0, 6).join('');
    const imports = (d.imports || []).map(i => `<code>${i.name}</code>`).slice(0, 6).join(', ');

    document.getElementById('moduleNodeDetailContent').innerHTML = `
    <div class="detail-title">${d.path}</div>
    <div class="detail-row"><span class="detail-key">Language</span><span class="detail-val">${d.language || '—'}</span></div>
    <div class="detail-row"><span class="detail-key">Layer</span><span class="detail-val">${d.architecture_layer || '—'}</span></div>
    <div class="detail-row"><span class="detail-key">Domain</span><span class="detail-val">${d.domain_cluster || '—'}</span></div>
    <div class="detail-row"><span class="detail-key">Complexity</span><span class="detail-val">${(d.complexity_score || 0).toFixed(1)}</span></div>
    <div class="detail-row"><span class="detail-key">Velocity</span><span class="detail-val">${(d.change_velocity_30d || 0).toFixed(1)}/mo</span></div>
    <div class="detail-row"><span class="detail-key">PageRank</span><span class="detail-val">${(d.pagerank_score || 0).toFixed(4)}</span></div>
    <div class="detail-row"><span class="detail-key">Arch Hub</span><span class="detail-val">${d.is_architectural_hub ? '✅ Yes' : 'No'}</span></div>
    <div class="detail-row"><span class="detail-key">Dead Code</span><span class="detail-val">${d.is_dead_code_candidate ? '☠️ Yes' : 'No'}</span></div>
    <div class="detail-row"><span class="detail-key">Doc Drift</span><span class="detail-val">${d.documentation_drift === true ? '⚠️ Yes' : d.documentation_drift === false ? 'OK' : '—'}</span></div>
    ${d.last_modified ? `<div class="detail-row"><span class="detail-key">Last Modified</span><span class="detail-val">${d.last_modified}</span></div>` : ''}
    ${d.purpose_statement ? `<div class="detail-purpose">${d.purpose_statement}</div>` : ''}
    ${funcs ? `<div class="detail-section">Public Functions</div>${funcs}` : ''}
    ${imports ? `<div class="detail-section">Key Imports</div><div style="font-size:11px;color:var(--text-secondary)">${imports}</div>` : ''}
  `;
}

document.getElementById('closeModuleDetail').addEventListener('click', () => {
    document.getElementById('moduleNodeDetail').classList.add('hidden');
});
document.getElementById('graphSearch').addEventListener('input', () => {
    if (state.moduleGraph) renderModuleGraph(state.moduleGraph);
});
document.getElementById('filterHubsOnly').addEventListener('change', () => {
    if (state.moduleGraph) renderModuleGraph(state.moduleGraph);
});
document.getElementById('filterHideInfo').addEventListener('change', () => {
    if (state.moduleGraph) renderModuleGraph(state.moduleGraph);
});

// ── Lineage Graph ─────────────────────────────────────────────────────────
async function loadLineageGraph() {
    if (!state.lineageGraph) {
        setLoading(true);
        state.lineageGraph = await apiFetch('/api/lineage-graph');
        setLoading(false);
    }
    if (!state.lineageGraph) return;
    renderLineageGraph(state.lineageGraph);
}

function renderLineageGraph(graph) {
    const search = document.getElementById('lineageSearch').value.toLowerCase();
    const typeFilter = document.getElementById('lineageLayerFilter').value;

    // Normalize nodes — data + transformations
    let rawNodes = graph.nodes;
    let nodeList = [];
    if (Array.isArray(rawNodes)) {
        nodeList = rawNodes;
    } else if (rawNodes && typeof rawNodes === 'object') {
        nodeList = [...(rawNodes.data || []), ...(rawNodes.transformations || [])];
    }

    let nodes = nodeList.map(n => ({ ...n, id: n.identity || n.name }));
    let edges = (graph.edges || []).map(e => ({ source: e.source, target: e.target, type: e.type }));

    if (search) nodes = nodes.filter(n => (n.id || '').toLowerCase().includes(search) || (n.name || '').includes(search));
    if (typeFilter) nodes = nodes.filter(n => (n.type || '').includes(typeFilter));

    const nodeIds = new Set(nodes.map(n => n.id));
    edges = edges.filter(e => nodeIds.has(e.source) && nodeIds.has(e.target));

    document.getElementById('lineageNodeCount').textContent = `${nodes.length} nodes, ${edges.length} edges`;

    const nodeColor = d => {
        if (d.type === 'PYTHON_SCRIPT' || d.type === 'DBT_MODEL' || d.type === 'AIRFLOW_TASK') return '#f59e0b';
        return '#10b981';
    };
    const nodeRadius = d => {
        return (d.role === 'SOURCE' || d.role === 'TERMINAL') ? 8 : 5;
    };
    const labelFn = d => (d.canonical_name || d.name || '').split(':').pop().split('/').pop().slice(0, 16);
    const tooltipFn = d => `
    <strong>${d.canonical_name || d.name}</strong><br/>
    <span style="color:#7b93c2">Type: ${d.type || '?'} | NS: ${d.namespace || '?'}</span>
    ${d.role ? `<br/>Role: <span style="color:${d.role === 'SOURCE' ? '#10b981' : d.role === 'TERMINAL' ? '#f43f5e' : '#f59e0b'}">${d.role}</span>` : ''}
    ${d.purpose_statement ? `<br/><em style="font-size:11px;color:#7b93c2">${d.purpose_statement.substring(0, 70)}…</em>` : ''}
  `;
    const clickFn = d => showLineageDetail(d);

    createForceGraph('lineageGraphSvg', 'lineageGraphContainer', nodes, edges, nodeColor, nodeRadius, labelFn, tooltipFn, clickFn);
}

function showLineageDetail(d) {
    const panel = document.getElementById('lineageNodeDetail');
    panel.classList.remove('hidden');
    document.getElementById('lineageNodeDetailContent').innerHTML = `
    <div class="detail-title">${d.canonical_name || d.name}</div>
    <div class="detail-row"><span class="detail-key">Type</span><span class="detail-val">${d.type || '—'}</span></div>
    <div class="detail-row"><span class="detail-key">Namespace</span><span class="detail-val">${d.namespace || '—'}</span></div>
    <div class="detail-row"><span class="detail-key">Role</span><span class="detail-val">${d.role || '—'}</span></div>
    <div class="detail-row"><span class="detail-key">Format</span><span class="detail-val">${d.format || '—'}</span></div>
    <div class="detail-row"><span class="detail-key">Environment</span><span class="detail-val">${d.environment || '—'}</span></div>
    <div class="detail-row"><span class="detail-key">Confidence</span><span class="detail-val">${(d.dataset_type_confidence || 1).toFixed(2)}</span></div>
    ${d.purpose_statement ? `<div class="detail-purpose">${d.purpose_statement}</div>` : ''}
  `;
}

document.getElementById('closeLineageDetail').addEventListener('click', () => {
    document.getElementById('lineageNodeDetail').classList.add('hidden');
});
document.getElementById('lineageSearch').addEventListener('input', () => {
    if (state.lineageGraph) renderLineageGraph(state.lineageGraph);
});
document.getElementById('lineageLayerFilter').addEventListener('change', () => {
    if (state.lineageGraph) renderLineageGraph(state.lineageGraph);
});

// ── Navigator ─────────────────────────────────────────────────────────────
function appendNavMessage(text, role) {
    const msgs = document.getElementById('navMessages');
    const div = document.createElement('div');
    div.className = `nav-msg nav-msg-${role}`;

    if (role === 'bot') {
        // Parse markdown-ish formatting for bot messages
        let formatted = text
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            .replace(/^## (.+)$/gm, '<strong style="font-size:13px;color:var(--cyan)">$1</strong>')
            .replace(/^### (.+)$/gm, '<strong style="color:var(--purple)">$1</strong>')
            .replace(/^\| .+$/gm, m => `<span style="font-family:var(--font-mono);border-bottom:1px solid var(--border);display:block">${m}</span>`);
        div.innerHTML = formatted;
    } else {
        div.textContent = text;
    }

    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
    return div;
}

async function sendNavQuery(question) {
    if (!question.trim()) return;
    const input = document.getElementById('navInput');
    const sendBtn = document.getElementById('navSend');
    input.value = '';
    sendBtn.disabled = true;

    appendNavMessage(question, 'user');
    const thinking = appendNavMessage('Consulting the knowledge graph…', 'bot');
    thinking.classList.add('nav-msg-thinking');

    const result = await fetch(`${API}/api/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, repo_path: REPO_PATH }),
    }).then(r => r.json()).catch(() => null);

    thinking.remove();

    if (result?.answer) {
        appendNavMessage(result.answer, 'bot');
    } else {
        appendNavMessage('❌ Navigator error. Is the API server running?', 'bot');
    }
    sendBtn.disabled = false;
    input.focus();
}

document.getElementById('navSend').addEventListener('click', () => {
    sendNavQuery(document.getElementById('navInput').value);
});
document.getElementById('navInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendNavQuery(e.target.value);
    }
});
$$('.example-chip').forEach(chip => {
    chip.addEventListener('click', () => sendNavQuery(chip.dataset.q));
});

// ── Artifacts ─────────────────────────────────────────────────────────────
async function loadArtifact(type) {
    const endpoint = type === 'codebase' ? '/api/artifacts/codebase' : '/api/artifacts/onboarding';
    const content = document.getElementById('artifactContent');
    content.innerHTML = '<p class="placeholder-text">Loading…</p>';
    const data = await apiFetch(endpoint);
    if (data?.content) {
        content.innerHTML = marked.parse(data.content);
    } else {
        content.innerHTML = `<p class="placeholder-text">Artifact not found. Run analysis first.</p>`;
    }
}

$$('.artifact-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        $$('.artifact-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        loadArtifact(tab.dataset.artifact);
    });
});

// ── Trace Log ─────────────────────────────────────────────────────────────
async function loadTrace() {
    const data = await apiFetch('/api/trace');
    const el = document.getElementById('traceLog');
    const filter = document.getElementById('traceSearch').value.toLowerCase();

    if (!data?.events?.length) {
        el.innerHTML = '<p class="placeholder-text">No trace events found.</p>';
        return;
    }

    const events = data.events.filter(e =>
        !filter ||
        (e.agent || '').toLowerCase().includes(filter) ||
        (e.event_type || '').toLowerCase().includes(filter) ||
        (e.target_file || '').toLowerCase().includes(filter)
    );

    el.innerHTML = events.map(e => {
        const time = formatTime(e.timestamp);
        const agent = e.agent || '?';
        return `
      <div class="trace-event">
        <span class="trace-time">${time}</span>
        <span class="trace-agent agent-${agent}">${agent}</span>
        <span class="trace-type">${e.event_type || '?'}</span>
        <span class="trace-target">${e.target_file || e.metadata?.error || '—'}</span>
      </div>`;
    }).join('');
}

document.getElementById('traceRefresh').addEventListener('click', loadTrace);
document.getElementById('traceSearch').addEventListener('input', loadTrace);

// ── Window resize — redraw graphs ─────────────────────────────────────────
let resizeTimer;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        if (state.moduleGraph && $('#tab-module-graph.active')) renderModuleGraph(state.moduleGraph);
        if (state.lineageGraph && $('#tab-lineage-graph.active')) renderLineageGraph(state.lineageGraph);
    }, 200);
});

// ── Boot ──────────────────────────────────────────────────────────────────
(async function boot() {
    // Try to detect repo path from URL param
    const params = new URLSearchParams(window.location.search);
    const rp = params.get('repo');
    if (rp) {
        REPO_PATH = rp;
        document.getElementById('repoPathInput').value = rp;
    }

    await initDashboard();
})();

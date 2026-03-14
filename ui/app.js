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
    const t = Date.now();
    const url = REPO_PATH
        ? `${API}${endpoint}${sep}repo_path=${encodeURIComponent(REPO_PATH)}&_t=${t}`
        : `${API}${endpoint}${sep}_t=${t}`;
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

    // Lazy-load or re-render tab data (delay slightly so container dimensions are ready)
    setTimeout(() => {
        if (tab === 'module-graph') loadModuleGraph();
        if (tab === 'lineage-graph') loadLineageGraph();
    }, 50);
    if (tab === 'artifacts') loadArtifact($('.artifact-tab.active')?.dataset.artifact || 'codebase');
    if (tab === 'trace') loadTrace();
}

$$('.nav-item').forEach(el => el.addEventListener('click', () => switchTab(el.dataset.tab)));

// ── Repo selector (supports local paths AND remote git URLs) ───────────────
function isRemoteUrl(s) {
    s = s.trim();
    return s.startsWith('http://') || s.startsWith('https://') ||
        s.startsWith('git@') || s.startsWith('git://');
}

function setCloneStatus(msg, type = '') {
    const el = document.getElementById('cloneStatus');
    if (!el) return;
    el.textContent = msg;
    el.className = `clone-status ${type}`;
    el.classList.toggle('hidden', !msg);
}

async function handleSetRepo() {
    const raw = document.getElementById('repoPathInput').value.trim();
    if (!raw) return;

    const btn = document.getElementById('setRepoBtn');
    btn.disabled = true;

    if (isRemoteUrl(raw)) {
        // ── Remote URL: clone first ────────────────────────────────
        const repoName = raw.replace(/\.git$/, '').split('/').pop();
        setCloneStatus(`⏳ Cloning ${repoName}…`, 'cloning');

        const response = await fetch(`${API}/api/clone`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: raw }),
        });

        const res = await response.json().catch(() => ({ detail: 'Failed to parse server response' }));

        if (!response.ok) {
            const errorMsg = res.detail || 'Unknown cloning error';
            setCloneStatus(`❌ ${errorMsg}`, 'error');
            console.error("[Clone] Error:", res);
            btn.disabled = false;
            return;
        }

        const cached = res.cached ? ' (cached)' : '';
        setCloneStatus(`✅ Cloned → ${res.repo_name}${cached}`, 'cloned');
        // Show local path in the input so user knows what was set
        document.getElementById('repoPathInput').value = res.path;
        // Auto-dismiss after 4 s
        setTimeout(() => setCloneStatus('', ''), 4000);
        REPO_PATH = res.path;
    } else {
        // ── Local path ─────────────────────────────────────────────
        REPO_PATH = raw;
        setCloneStatus('', '');
    }

    state.moduleGraph = null;
    state.lineageGraph = null;
    state.status = null;
    $('#artifactContent').innerHTML = '<p class="placeholder-text">Select an artifact to view</p>';
    btn.disabled = false;
    initDashboard();
}

document.getElementById('setRepoBtn').addEventListener('click', handleSetRepo);
document.getElementById('repoPathInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleSetRepo();
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

        // Update repo indicator
        const ri = $('#currentRepoIndicator');
        if (ri) {
            ri.textContent = statusData.repo_path || REPO_PATH || 'Local Server Root';
            ri.title = statusData.repo_path || REPO_PATH || '';
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
    const llmEnabled = document.getElementById('llmEnabledCheckbox').checked;
    const semanticDepth = document.getElementById('semanticDepthSelect').value;

    btn.disabled = true;
    status.textContent = '⚡ Analysis running…';
    status.classList.remove('hidden');

    const result = await fetch(`${API}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            repo_path: REPO_PATH || '.',
            llm_enabled: llmEnabled,
            semantic_depth: semanticDepth
        }),
    }).then(r => r.json()).catch(() => null);

    if (result?.status === 'started') {
        status.textContent = '✅ Analysis running in background…';
        
        let attempts = 0;
        const maxAttempts = 20;
        const initialTimestamp = state.status?.timestamp;

        const poll = async () => {
            attempts++;
            const currentStatus = await apiFetch('/api/status');
            
            if (currentStatus && currentStatus.timestamp !== initialTimestamp) {
                status.textContent = '✨ Analysis complete! Refreshing…';
                state.moduleGraph = null;
                state.lineageGraph = null;
                await initDashboard();
                if ($('#tab-artifacts.active')) {
                    loadArtifact($('.artifact-tab.active')?.dataset.artifact || 'codebase');
                }
                setTimeout(() => {
                    btn.disabled = false;
                    status.classList.add('hidden');
                }, 2000);
            } else if (attempts < maxAttempts) {
                status.textContent = `⚡ Analysis running… (Attempt ${attempts}/${maxAttempts})`;
                setTimeout(poll, 4000);
            } else {
                status.textContent = '⚠️ Analysis taking longer than expected. Please check back later.';
                btn.disabled = false;
                initDashboard();
            }
        };

        setTimeout(poll, 5000);
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

    let W = container.clientWidth;
    let H = container.clientHeight;

    // Fallback if container is hidden/collapsed
    if (W === 0 || H === 0) {
        const main = document.querySelector('.main-content');
        if (main) {
            W = main.clientWidth - 48; // accounting for padding
            H = main.clientHeight - 120; // accounting for header/toolbar
        }
    }

    // Hard fallback
    if (W <= 0) W = window.innerWidth - 300;
    if (H <= 0) H = window.innerHeight - 200;

    console.log(`[Graph] Drawing ${svgId} in ${containerId}: ${W}x${H}, ${nodes.length} nodes, ${links.length} links`);
    svg.attr('viewBox', `0 0 ${W} ${H}`);

    const g = svg.append('g');

    // Zoom + pan
    svg.call(d3.zoom().scaleExtent([0.1, 8]).on('zoom', e => g.attr('transform', e.transform)));

    // Tooltip div
    const tooltip = document.getElementById(`${svgId.replace('Svg', 'Tooltip')}`);

    // Defs: arrow + glow filter
    const defs = svg.append('defs');
    defs.append('marker')
        .attr('id', `arrow-${svgId}`)
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 20).attr('refY', 0)
        .attr('markerWidth', 5).attr('markerHeight', 5)
        .attr('orient', 'auto')
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', '#4a6090');

    const glow = defs.append('filter').attr('id', `glow-${svgId}`);
    glow.append('feGaussianBlur').attr('stdDeviation', '3').attr('result', 'coloredBlur');
    const merge = glow.append('feMerge');
    merge.append('feMergeNode').attr('in', 'coloredBlur');
    merge.append('feMergeNode').attr('in', 'SourceGraphic');

    const sim = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.id).distance(100).strength(0.4))
        .force('charge', d3.forceManyBody().strength(-280))
        .force('center', d3.forceCenter(W / 2, H / 2))
        .force('collision', d3.forceCollide().radius(d => nodeRadius(d) + 12));

    // ── Edges ──────────────────────────────────────────────────────────
    const link = g.append('g')
        .selectAll('line')
        .data(links)
        .join('line')
        .attr('stroke-width', 1.5)
        .attr('stroke', '#3d5a8a')
        .attr('stroke-opacity', 0.75)
        .attr('marker-end', `url(#arrow-${svgId})`);

    // ── Nodes ──────────────────────────────────────────────────────────
    // Outer glow ring
    const ring = g.append('g')
        .selectAll('circle')
        .data(nodes)
        .join('circle')
        .attr('r', d => nodeRadius(d) + 4)
        .attr('fill', 'none')
        .attr('stroke', d => nodeColor(d))
        .attr('stroke-width', 1.5)
        .attr('stroke-opacity', 0.25)
        .attr('pointer-events', 'none');

    const node = g.append('g')
        .selectAll('circle')
        .data(nodes)
        .join('circle')
        .attr('r', d => nodeRadius(d))
        .attr('fill', d => nodeColor(d))
        .attr('fill-opacity', 0.92)
        .attr('stroke', d => nodeColor(d))
        .attr('stroke-width', 2)
        .attr('stroke-opacity', 0.6)
        .style('cursor', 'pointer')
        .call(d3.drag()
            .on('start', (e, d) => { if (!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
            .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y; })
            .on('end', (e, d) => { if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null; })
        )
        .on('mouseover', (e, d) => {
            d3.select(e.currentTarget)
                .attr('filter', `url(#glow-${svgId})`)
                .attr('stroke-opacity', 1)
                .attr('r', nodeRadius(d) + 2);
            tooltip.innerHTML = tooltipFn(d);
            tooltip.classList.remove('hidden');
        })
        .on('mousemove', (e) => {
            tooltip.style.left = (e.offsetX + 14) + 'px';
            tooltip.style.top = (e.offsetY - 10) + 'px';
        })
        .on('mouseout', (e, d) => {
            d3.select(e.currentTarget)
                .attr('filter', null)
                .attr('stroke-opacity', 0.6)
                .attr('r', nodeRadius(d));
            tooltip.classList.add('hidden');
        })
        .on('click', (e, d) => { e.stopPropagation(); if (clickFn) clickFn(d); });

    // ── Labels with pill background ────────────────────────────────────
    const labelG = g.append('g').selectAll('g').data(nodes).join('g').attr('pointer-events', 'none');

    // Background pill rect (sized dynamically after text render)
    const labelBg = labelG.append('rect')
        .attr('rx', 3).attr('ry', 3)
        .attr('fill', 'rgba(8,14,28,0.78)')
        .attr('stroke', 'rgba(100,140,200,0.18)')
        .attr('stroke-width', 0.5);

    const labelText = labelG.append('text')
        .text(d => labelFn(d))
        .attr('font-size', 11)
        .attr('font-family', 'Inter, system-ui, sans-serif')
        .attr('fill', '#d0ddf5')
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'middle');

    sim.on('tick', () => {
        link
            .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
        node.attr('cx', d => d.x).attr('cy', d => d.y);
        ring.attr('cx', d => d.x).attr('cy', d => d.y);
        labelG.attr('transform', d => `translate(${d.x},${d.y + nodeRadius(d) + 13})`);

        // Size the background pill after text is placed
        labelText.each(function () {
            try {
                const bb = this.getBBox();
                const pad = 3;
                d3.select(this.previousElementSibling)
                    .attr('x', bb.x - pad)
                    .attr('y', bb.y - pad)
                    .attr('width', bb.width + pad * 2)
                    .attr('height', bb.height + pad * 2);
            } catch (_) { }
        });
    });

    return { sim, node, link, labelText, labelBg, g };
}

// ── Module Graph ──────────────────────────────────────────────────────────
async function loadModuleGraph() {
    if (!state.moduleGraph) {
        setLoading(true);
        state.moduleGraph = await apiFetch('/api/module-graph');
        setLoading(false);
    }
    if (!state.moduleGraph) {
        console.warn("[ModuleGraph] No data in state, skipping render");
        return;
    }
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

    document.getElementById('graphNodeCount').textContent = `${nodes.length} nodes, ${edges.length} edges`;

    // ── Vivid, high-contrast colour palette ──────────────────────────
    const nodeColor = d => {
        if (d.is_architectural_hub) return '#c084fc'; // vivid purple
        if (d.is_dead_code_candidate) return '#f87171'; // vivid red
        if (d.is_high_velocity) return '#fb923c'; // orange
        if (d.is_informational) return '#4b6fa8'; // muted blue-slate
        // colour by language
        const lang = (d.language || '').toLowerCase();
        if (lang === 'python') return '#34d399'; // green
        if (lang === 'sql') return '#38bdf8'; // sky blue
        if (lang === 'yaml' || lang === 'json') return '#a78bfa'; // lavender
        return '#60a5fa'; // default blue
    };

    // ── Bigger nodes — min 8px so they're always clickable ───────────
    const nodeRadius = d => {
        if (d.is_architectural_hub) return 14;
        if (d.is_high_velocity) return 11;
        return 8;
    };

    // ── Short filename label ─────────────────────────────────────────
    const labelFn = d => {
        const parts = (d.path || d.identity || '').split('/');
        return parts[parts.length - 1] || d.identity;
    };

    const tooltipFn = d => `
        <strong>${d.identity}</strong><br/>
        <span style="color:#94afd4">${d.path}</span><br/>
        Language: <b>${d.language || '?'}</b> | Layer: ${d.architecture_layer || '—'}<br/>
        Complexity: ${(d.complexity_score || 0).toFixed(1)} &nbsp;|&nbsp; PageRank: ${(d.pagerank_score || 0).toFixed(3)}
        ${d.purpose_statement ? `<br/><em style="color:#94afd4;font-size:11px">${d.purpose_statement.substring(0, 90)}…</em>` : ''}
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
    console.log("[LineageGraph] Attempting to load...");
    try {
        if (!state.lineageGraph) {
            setLoading(true);
            state.lineageGraph = await apiFetch('/api/lineage-graph');
            setLoading(false);
        }
        if (!state.lineageGraph) {
            console.warn("[LineageGraph] No data received from server");
            $('#lineageNodeCount').textContent = "No data found. Run analysis first.";
            return;
        }
        renderLineageGraph(state.lineageGraph);
    } catch (e) {
        setLoading(false);
        console.error("[LineageGraph] Load error:", e);
        $('#lineageNodeCount').textContent = "Error loading graph data.";
    }
}

function renderLineageGraph(graph) {
    const search = document.getElementById('lineageSearch').value.toLowerCase();
    const typeFilter = document.getElementById('lineageLayerFilter').value;

    // Normalize nodes — handle multiple schema versions (Phase 1, 2, 3)
    let nodeList = [];

    // 1. Try top-level data_nodes/transformation_nodes (LineageGraph schema)
    if (graph.data_nodes || graph.transformation_nodes) {
        nodeList = [...(graph.data_nodes || []), ...(graph.transformation_nodes || [])];
    }
    // 2. Try nested nodes.data/nodes.transformations
    else if (graph.nodes && typeof graph.nodes === 'object' && !Array.isArray(graph.nodes)) {
        nodeList = [...(graph.nodes.data || []), ...(graph.nodes.transformations || [])];
    }
    // 3. Try top-level nodes array (ModuleGraph schema)
    else if (Array.isArray(graph.nodes)) {
        nodeList = graph.nodes;
    }

    console.log(`[LineageGraph] Resolved ${nodeList.length} nodes from keys:`, Object.keys(graph));


    let nodes = nodeList.map(n => ({ ...n, id: n.identity || n.name }));
    let edges = (graph.edges || []).map(e => ({ source: e.source, target: e.target, type: e.type }));

    console.log(`[LineageGraph] Loaded: ${nodes.length} nodes, ${edges.length} edges`);
    if (search) nodes = nodes.filter(n => (n.id || '').toLowerCase().includes(search) || (n.name || '').toLowerCase().includes(search));

    if (typeFilter) {
        if (typeFilter === 'file') {
            nodes = nodes.filter(n => ['python_script', 'dbt_model', 'file_dataset'].includes((n.type || '').toLowerCase()));
        } else {
            nodes = nodes.filter(n => (n.type || '').toLowerCase().includes(typeFilter.toLowerCase()));
        }
    }

    const nodeIds = new Set(nodes.map(n => n.id));
    edges = edges.filter(e => nodeIds.has(e.source) && nodeIds.has(e.target));

    console.log(`[LineageGraph] Filtered: ${nodes.length} nodes, ${edges.length} edges (Search: "${search}", Filter: "${typeFilter}")`);
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

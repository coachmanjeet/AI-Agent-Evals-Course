/* Trace Viewer — static OTel trace explorer for error analysis (Week 1 tool).
   No backend. Upload OTLP JSON, browse span trees, annotate failure modes,
   export annotations as the seed of an eval dataset. */

const LS_KEY = 'tv101:annotations';

const FAILURE_MODES = [
  'wrong_order_status', 'refund_policy_misquote', 'over_refund',
  'missing_escalation', 'pii_leak', 'tone_failure', 'tool_misuse',
  'ignored_constraint', 'stale_data', 'refused_valid_query',
  'warranty_misinfo', 'prompt_injection_compliance', 'jailbreak_compliance',
  'hallucinated_policy',
];
const NO_FAILURE = 'no_failure';

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
const MISSING = '—';

const state = {
  traces: [],
  byId: {},
  selectedTraceId: null,
  selectedSpanId: null,
  collapsed: new Set(),          // spanIds collapsed in the tree
  annotations: loadAnnotations(),
  filters: { q: '', review: 'all', mode: 'all', errorsOnly: false },
};

/* ---------------- persistence ---------------- */
function loadAnnotations() {
  try {
    const raw = localStorage.getItem(LS_KEY);
    const d = raw ? JSON.parse(raw) : {};
    return (d && typeof d === 'object') ? d : {};
  } catch { return {}; }
}
function saveAnnotations() {
  try { localStorage.setItem(LS_KEY, JSON.stringify(state.annotations)); } catch {}
}

/* ---------------- OTel parsing (liberal) ---------------- */
function attrPrimitive(v) {
  if (v === null || v === undefined) return null;
  if (typeof v === 'object') {
    if ('stringValue' in v) return v.stringValue;
    if ('boolValue' in v) return !!v.boolValue;
    if ('intValue' in v) return Number(v.intValue);
    if ('doubleValue' in v) return Number(v.doubleValue);
    if ('bytesValue' in v) return `[bytes:${String(v.bytesValue).length}]`;
    if ('arrayValue' in v && v.arrayValue && Array.isArray(v.arrayValue.values))
      return v.arrayValue.values.map(attrPrimitive);
    if ('kvlistValue' in v && v.kvlistValue && Array.isArray(v.kvlistValue.values))
      return flattenAttrs(v.kvlistValue.values);
    return JSON.stringify(v);
  }
  return v;
}

function flattenAttrs(attrs) {
  const out = {};
  if (!Array.isArray(attrs)) return out;
  for (const a of attrs) {
    if (!a || typeof a.key !== 'string') continue;
    out[a.key] = attrPrimitive(a.value);
  }
  return out;
}

function toMs(t) {
  if (t === null || t === undefined || t === '') return null;
  if (typeof t === 'number' || /^\d+$/.test(String(t).trim())) {
    const n = Number(t);
    if (!Number.isFinite(n)) return null;
    // nanoseconds -> ms (OTLP uses nanos; micros would be < 1e14 for sane dates)
    return n > 1e14 ? n / 1e6 : n / 1e3;
  }
  const d = Date.parse(t);
  return Number.isNaN(d) ? null : d;
}

function fmtTime(ms) {
  if (ms === null) return MISSING;
  try { return new Date(ms).toISOString(); } catch { return MISSING; }
}

function isErrorSpan(span) {
  const c = span.status && span.status.code;
  return c === 2 || c === 'ERROR' || c === 'Error';
}

function extractSpans(data) {
  // Returns { spans, source } or throws a friendly Error.
  if (Array.isArray(data)) return { spans: data, source: 'array' };
  if (data && typeof data === 'object') {
    if (Array.isArray(data.spans)) return { spans: data.spans, source: 'flat' };
    if (Array.isArray(data.resourceSpans)) {
      const spans = [];
      for (const rs of data.resourceSpans) {
        const resAttrs = flattenAttrs(rs.resource && rs.resource.attributes);
        for (const ss of (rs.scopeSpans || [])) {
          const scopeName = ss.scope && ss.scope.name;
          for (const sp of (ss.spans || [])) {
            const copy = { ...sp };
            copy._resource = resAttrs;
            if (scopeName) copy._scope = scopeName;
            spans.push(copy);
          }
        }
      }
      return { spans, source: 'otlp' };
    }
    // single span object?
    if (data.traceId && data.spanId) return { spans: [data], source: 'single' };
  }
  throw new Error('unrecognized');
}

function parseUpload(data) {
  let extracted;
  try {
    extracted = extractSpans(data);
  } catch {
    throw friendlyParseError();
  }
  const raw = extracted.spans;
  if (!raw.length) throw friendlyParseError('empty');
  const traces = buildTraces(raw);
  if (!traces.length) throw friendlyParseError('nospan');
  return traces;
}

function friendlyParseError(kind) {
  const msg = document.createElement('div');
  msg.innerHTML =
    '<strong>Couldn\'t read that file as OTel traces.</strong>' +
    (kind === 'empty' ? ' The file parsed as JSON, but it contained <strong>zero spans</strong>.'
      : kind === 'nospan' ? ' The spans found had no usable <code>traceId</code>/<code>spanId</code>.'
      : ' It didn\'t match any recognized shape.') +
    '<ul><li>Expected <strong>OTLP JSON</strong>: <code>{"resourceSpans":[{"resource":{},"scopeSpans":[{"spans":[...]}]}]}</code></li>' +
    '<li>…or a flat <code>{"spans":[...]}</code>, a bare <code>[...]</code> span array, or a single span object.</li>' +
    '<li>Each span needs <code>traceId</code>, <code>spanId</code>, <code>name</code>, and start/end times ' +
    '(<code>startTimeUnixNano</code>/<code>endTimeUnixNano</code> or ISO strings).</li></ul>';
  const err = new Error('parse');
  err.html = msg.innerHTML;
  return err;
}

function buildTraces(rawSpans) {
  const byTrace = new Map();
  for (const sp of rawSpans) {
    if (!sp || typeof sp !== 'object') continue;
    const traceId = sp.traceId, spanId = sp.spanId;
    if (!traceId || !spanId) continue;
    const startMs = toMs(sp.startTimeUnixNano ?? sp.startTime);
    const endMs = toMs(sp.endTimeUnixNano ?? sp.endTime);
    const node = {
      traceId: String(traceId), spanId: String(spanId),
      parentSpanId: sp.parentSpanId ? String(sp.parentSpanId) : null,
      name: sp.name || '(unnamed span)',
      kind: sp.kind ?? null,
      startMs, endMs,
      durationMs: (startMs !== null && endMs !== null && endMs >= startMs) ? endMs - startMs : null,
      attributes: flattenAttrs(sp.attributes),
      status: sp.status || {},
      events: (Array.isArray(sp.events) ? sp.events : []).map(e => ({
        name: e.name || '(unnamed event)',
        timeMs: toMs(e.timeUnixNano ?? e.time),
        attributes: flattenAttrs(e.attributes),
      })),
      error: false, children: [],
      _resource: sp._resource || {}, _scope: sp._scope || null,
    };
    node.error = isErrorSpan({ status: node.status });
    if (!byTrace.has(node.traceId)) byTrace.set(node.traceId, []);
    byTrace.get(node.traceId).push(node);
  }
  const traces = [];
  for (const [traceId, nodes] of byTrace) {
    const bySpan = new Map(nodes.map(n => [n.spanId, n]));
    const roots = [];
    for (const n of nodes) {
      const p = n.parentSpanId && bySpan.get(n.parentSpanId);
      if (p) p.children.push(n); else roots.push(n);
    }
    // order children by start time
    const sortTree = n => { n.children.sort((a, b) => (a.startMs ?? 0) - (b.startMs ?? 0)); n.children.forEach(sortTree); };
    roots.sort((a, b) => (a.startMs ?? 0) - (b.startMs ?? 0));
    roots.forEach(sortTree);
    const starts = nodes.map(n => n.startMs).filter(v => v !== null);
    const ends = nodes.map(n => n.endMs).filter(v => v !== null);
    const rootName = roots.length ? roots[0].name : '(no root)';
    // precomputed lowercase search blob: names, ids, all attribute values, events
    const blobParts = [traceId, rootName];
    for (const n of nodes) {
      blobParts.push(n.name, n.spanId);
      for (const v of Object.values(n.attributes)) {
        blobParts.push(typeof v === 'object' ? JSON.stringify(v) : String(v));
      }
      for (const e of n.events) {
        blobParts.push(e.name);
        for (const v of Object.values(e.attributes)) blobParts.push(String(v));
      }
    }
    traces.push({
      traceId,
      nodes, roots,
      spanCount: nodes.length,
      startMs: starts.length ? Math.min(...starts) : null,
      endMs: ends.length ? Math.max(...ends) : null,
      durationMs: (starts.length && ends.length) ? Math.max(...ends) - Math.min(...starts) : null,
      hasError: nodes.some(n => n.error),
      rootName,
      searchBlob: blobParts.join(' ').toLowerCase(),
    });
  }
  traces.sort((a, b) => (b.startMs ?? 0) - (a.startMs ?? 0));
  return traces;
}

/* ---------------- helpers ---------------- */
function fmtDur(ms) {
  if (ms === null || ms === undefined) return MISSING;
  if (ms < 1) return `${ms.toFixed(2)} ms`;
  if (ms < 1000) return `${ms.toFixed(1)} ms`;
  return `${(ms / 1000).toFixed(2)} s`;
}
function shortId(id) { return id.length > 12 ? id.slice(0, 12) + '…' : id; }
function annotFor(traceId) { return state.annotations[traceId] || null; }
function reviewedCount() { return Object.keys(state.annotations).length; }

function download(filename, text, mime) {
  const blob = new Blob([text], { type: mime });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 500);
}

/* ---------------- filtering ---------------- */
function filteredTraces() {
  const f = state.filters;
  const q = f.q.trim().toLowerCase();
  return state.traces.filter(t => {
    if (f.errorsOnly && !t.hasError) return false;
    if (q && !t.searchBlob.includes(q)) return false;
    const a = annotFor(t.traceId);
    if (f.review === 'unreviewed' && a) return false;
    if (f.review === 'has_failure' && !(a && a.failure_mode && a.failure_mode !== NO_FAILURE)) return false;
    if (f.review === 'no_failure' && !(a && a.failure_mode === NO_FAILURE)) return false;
    if (f.mode !== 'all' && !(a && a.failure_mode === f.mode)) return false;
    return true;
  });
}

/* ---------------- trace list ---------------- */
function renderTraceList() {
  const list = $('[data-role="trace-list"]');
  const traces = filteredTraces();
  $('[data-role="trace-count"]').textContent = `${traces.length} shown`;
  if (!traces.length) {
    list.innerHTML = '<div class="tv-empty">No traces match these filters.</div>';
    return;
  }
  list.innerHTML = traces.map(t => {
    const a = annotFor(t.traceId);
    const sel = t.traceId === state.selectedTraceId ? ' is-selected' : '';
    return `<div class="tv-trace${sel}" data-trace="${esc(t.traceId)}" role="button" tabindex="0">
      <div class="tv-trace__id">${esc(shortId(t.traceId))}</div>
      <div class="tv-trace__name">${esc(t.rootName)}</div>
      <div class="tv-trace__meta">
        <span>${t.spanCount} spans</span><span>${fmtDur(t.durationMs)}</span>
        ${t.hasError ? '<span class="tv-badge tv-badge--err">error</span>' : '<span class="tv-badge tv-badge--ok">ok</span>'}
        ${a ? (a.failure_mode && a.failure_mode !== NO_FAILURE
          ? `<span class="tv-badge tv-badge--mode">${esc(a.failure_mode)}</span>`
          : '<span class="tv-badge tv-badge--reviewed">reviewed</span>') : ''}
      </div></div>`;
  }).join('');
}

/* ---------------- span tree ---------------- */
function barStyle(trace, node) {
  if (trace.durationMs === null || trace.durationMs <= 0 || node.startMs === null || node.durationMs === null)
    return 'left:0;width:100%;opacity:0.35';
  const left = Math.max(0, ((node.startMs - trace.startMs) / trace.durationMs) * 100);
  const width = Math.max(1.5, (node.durationMs / trace.durationMs) * 100);
  return `left:${left.toFixed(2)}%;width:${Math.min(100 - left, width).toFixed(2)}%`;
}

function renderTree() {
  const mount = $('[data-role="span-tree"]');
  const trace = state.byId[state.selectedTraceId];
  if (!trace) { mount.innerHTML = '<div class="tv-empty">Select a trace to see its spans.</div>'; return; }
  const rows = [];
  const walk = (node, depth) => {
    const collapsed = state.collapsed.has(node.spanId);
    const hasKids = node.children.length > 0;
    const sel = node.spanId === state.selectedSpanId ? ' is-selected' : '';
    const err = node.error ? ' is-error' : '';
    rows.push(`<div class="tv-span${sel}${err}" data-span="${esc(node.spanId)}" role="button" tabindex="0">
      <div class="tv-span__left" style="padding-left:${depth * 18}px">
        <button class="tv-caret${hasKids ? '' : ' tv-caret--leaf'}" data-caret="${esc(node.spanId)}" aria-label="toggle">▾</button>
        <span class="tv-span__dot"></span>
        <span class="tv-span__name">${esc(node.name)}</span>
      </div>
      <div class="tv-bar"><div class="tv-bar__fill" style="${barStyle(trace, node)}"></div></div>
      <div class="tv-span__dur">${fmtDur(node.durationMs)}</div>
    </div>`);
    if (!collapsed) node.children.forEach(c => walk(c, depth + 1));
  };
  trace.roots.forEach(r => walk(r, 0));
  mount.innerHTML = rows.join('') || '<div class="tv-empty">No spans in this trace.</div>';
  $('[data-role="trace-head"]').innerHTML =
    `<div class="tv-tracehead__id">trace ${esc(trace.traceId)}</div>
     <div class="tv-tracehead__name">${esc(trace.rootName)}</div>
     <div class="tv-trace__meta"><span>${trace.spanCount} spans</span><span>${fmtDur(trace.durationMs)}</span>
     ${trace.hasError ? '<span class="tv-badge tv-badge--err">error</span>' : '<span class="tv-badge tv-badge--ok">ok</span>'}</div>`;
}

function findNode(trace, spanId) {
  let found = null;
  const walk = n => { if (n.spanId === spanId) { found = n; return; } n.children.forEach(walk); };
  trace.roots.forEach(walk);
  return found;
}

/* ---------------- span detail ---------------- */
function attrRows(attributes) {
  const entries = Object.entries(attributes || {});
  if (!entries.length) return '<div class="tv-empty" style="padding:8px">No attributes.</div>';
  const rank = k => (k.startsWith('gen_ai.') ? 0 : k.startsWith('llm.') ? 1 : k.startsWith('tool.') ? 2 : 3);
  entries.sort((a, b) => rank(a[0]) - rank(b[0]) || (a[0] < b[0] ? -1 : 1));
  return entries.map(([k, v]) => {
    const val = v === null || v === undefined ? MISSING
      : (typeof v === 'object' ? JSON.stringify(v, null, 1) : String(v));
    return `<div class="tv-attr"><dl class="tv-kv"><dt>${esc(k)}</dt><dd>${esc(val)}</dd></dl></div>`;
  }).join('');
}

function renderDetail() {
  const mount = $('[data-role="span-detail"]');
  const trace = state.byId[state.selectedTraceId];
  const node = trace && findNode(trace, state.selectedSpanId);
  if (!node) { mount.innerHTML = '<div class="tv-empty">Click a span to inspect it.</div>'; return; }
  const st = node.status || {};
  const stLabel = st.code === 2 || st.code === 'ERROR' ? '<span class="tv-badge tv-badge--err">error</span>'
    : st.code === 1 || st.code === 'OK' ? '<span class="tv-badge tv-badge--ok">ok</span>' : MISSING;
  mount.innerHTML = `
    <div class="tv-detail__sec"><h4>Span</h4>
      <dl class="tv-kv">
        <dt>name</dt><dd>${esc(node.name)}</dd>
        <dt>span id</dt><dd>${esc(node.spanId)}</dd>
        <dt>trace id</dt><dd>${esc(node.traceId)}</dd>
        <dt>parent</dt><dd>${node.parentSpanId ? esc(node.parentSpanId) : MISSING}</dd>
        <dt>scope</dt><dd>${node._scope ? esc(node._scope) : MISSING}</dd>
        <dt>status</dt><dd>${stLabel}${st.message ? ' ' + esc(st.message) : ''}</dd>
        <dt>start</dt><dd>${fmtTime(node.startMs)}</dd>
        <dt>end</dt><dd>${fmtTime(node.endMs)}</dd>
        <dt>duration</dt><dd>${fmtDur(node.durationMs)}</dd>
      </dl></div>
    <div class="tv-detail__sec"><h4>Attributes (${Object.keys(node.attributes).length})</h4>${attrRows(node.attributes)}</div>
    <div class="tv-detail__sec"><h4>Events (${node.events.length})</h4>
      ${node.events.length ? node.events.map(e => `
        <div class="tv-event"><div class="tv-event__name">${esc(e.name)}</div>
        <div class="tv-event__time">${fmtTime(e.timeMs)}</div>${attrRows(e.attributes)}</div>`).join('')
        : '<div class="tv-empty" style="padding:8px">No events.</div>'}
    </div>`;
}

/* ---------------- annotation ---------------- */
function renderAnnotationBar() {
  const traceId = state.selectedTraceId;
  const sel = $('[data-role="annot-mode"]');
  const note = $('[data-role="annot-note"]');
  const a = traceId ? annotFor(traceId) : null;
  sel.value = a ? a.failure_mode : '';
  note.value = a ? (a.note || '') : '';
  $('[data-role="annot-saved"]').textContent = a ? `Saved ${new Date(a.ts).toLocaleString()}` : '';
}

function persistAnnotation() {
  const traceId = state.selectedTraceId;
  if (!traceId) return;
  const mode = $('[data-role="annot-mode"]').value;
  const note = $('[data-role="annot-note"]').value.trim();
  if (!mode && !note) {
    delete state.annotations[traceId];
  } else {
    state.annotations[traceId] = { failure_mode: mode || null, note, ts: new Date().toISOString() };
  }
  saveAnnotations();
  $('[data-role="annot-saved"]').textContent = state.annotations[traceId]
    ? `Saved ${new Date(state.annotations[traceId].ts).toLocaleString()}` : 'Cleared';
  renderTraceList();
  updateProgress();
}

function updateProgress() {
  const total = state.traces.length;
  const done = state.traces.filter(t => annotFor(t.traceId)).length;
  $('[data-role="progress"]').textContent = total ? `${done}/${total} traces reviewed` : '';
  const hasAny = done > 0;
  $('[data-role="export-json"]').disabled = !hasAny;
  $('[data-role="export-csv"]').disabled = !hasAny;
}

/* ---------------- export ---------------- */
function annotationRows() {
  return state.traces
    .filter(t => annotFor(t.traceId))
    .map(t => ({ traceId: t.traceId, ...(state.annotations[t.traceId]) }));
}
function exportJSON() {
  download('trace-annotations.json', JSON.stringify(annotationRows(), null, 2), 'application/json');
}
function exportCSV() {
  const rows = annotationRows();
  const q = v => `"${String(v ?? '').replace(/"/g, '""')}"`;
  const csv = ['trace_id,failure_mode,note,timestamp',
    ...rows.map(r => [q(r.traceId), q(r.failure_mode || ''), q(r.note || ''), q(r.ts || '')].join(','))].join('\n');
  download('trace-annotations.csv', csv, 'text/csv');
}

/* ---------------- load / errors ---------------- */
function showError(html) {
  $('[data-role="alert-mount"]').innerHTML = `<div class="tv-error" role="alert">${html}</div>`;
}
function clearError() { $('[data-role="alert-mount"]').innerHTML = ''; }

function setData(traces) {
  state.traces = traces;
  state.byId = Object.fromEntries(traces.map(t => [t.traceId, t]));
  state.collapsed.clear();
  state.selectedTraceId = null;
  state.selectedSpanId = null;
  state.filters = { q: '', review: 'all', mode: 'all', errorsOnly: false };
  $('[data-role="filter-q"]').value = '';
  $('[data-role="filter-review"]').value = 'all';
  $('[data-role="filter-mode"]').value = 'all';
  $('[data-role="filter-errors"]').checked = false;
  const show = traces.length > 0;
  $$('[data-role="panel-left"], [data-role="panel-center"], [data-role="panel-right"], [data-role="exportbar"]')
    .forEach(el => el.classList.toggle('tv-hidden', !show));
  $('[data-role="upload-zone"]').classList.toggle('tv-hidden', show);
  renderTraceList();
  renderTree();
  renderDetail();
  renderAnnotationBar();
  updateProgress();
  if (traces.length) selectTrace(traces[0].traceId);
}

function selectTrace(traceId) {
  state.selectedTraceId = traceId;
  state.selectedSpanId = null;
  state.collapsed.clear();
  renderTraceList();
  renderTree();
  renderDetail();
  renderAnnotationBar();
}

function selectSpan(spanId) {
  state.selectedSpanId = spanId;
  renderTree();
  renderDetail();
}

function loadFile(file) {
  clearError();
  const reader = new FileReader();
  reader.onload = () => {
    let data;
    try { data = JSON.parse(reader.result); }
    catch { showError('<strong>That file isn\'t valid JSON.</strong> Pick the JSON export of your traces and try again.'); return; }
    try {
      const traces = parseUpload(data);
      setData(traces);
    } catch (e) {
      showError(e.html || '<strong>Couldn\'t read that file.</strong>');
    }
  };
  reader.onerror = () => showError('<strong>Couldn\'t read that file.</strong> Try again.');
  reader.readAsText(file);
}

async function loadSample() {
  clearError();
  try {
    const res = await fetch('./sample-pronto-otel-traces.json');
    if (!res.ok) throw new Error('http ' + res.status);
    setData(parseUpload(await res.json()));
  } catch {
    showError('<strong>Couldn\'t load the sample file.</strong> Serve this folder over HTTP ' +
      '(<code>cd docs &amp;&amp; python3 -m http.server</code>) — <code>fetch</code> doesn\'t work from <code>file://</code>.');
  }
}

/* ---------------- wiring ---------------- */
function init() {
  // failure-mode dropdowns
  const modeOptions = ['', NO_FAILURE, ...FAILURE_MODES].map(m =>
    `<option value="${m}">${m === '' ? 'Choose failure mode…' : m}</option>`).join('');
  $('[data-role="annot-mode"]').innerHTML = modeOptions;
  $('[data-role="filter-mode"]').innerHTML = '<option value="all">All failure modes</option>' +
    [NO_FAILURE, ...FAILURE_MODES].map(m => `<option value="${m}">${m}</option>`).join('');

  // upload
  const fileInput = $('[data-role="file-input"]');
  $$('[data-role="upload-btn"], [data-role="upload-btn-2"]').forEach(b =>
    b.addEventListener('click', () => fileInput.click()));
  fileInput.addEventListener('change', () => { if (fileInput.files[0]) loadFile(fileInput.files[0]); fileInput.value = ''; });
  $$('[data-role="load-sample"], [data-role="load-sample-2"]').forEach(b =>
    b.addEventListener('click', loadSample));

  // drag & drop
  const zone = $('[data-role="upload-zone"]');
  ['dragenter', 'dragover'].forEach(ev => zone.addEventListener(ev, e => { e.preventDefault(); zone.classList.add('is-drag'); }));
  ['dragleave', 'drop'].forEach(ev => zone.addEventListener(ev, e => { e.preventDefault(); zone.classList.remove('is-drag'); }));
  zone.addEventListener('drop', e => { const f = e.dataTransfer.files[0]; if (f) loadFile(f); });

  // filters
  $('[data-role="filter-q"]').addEventListener('input', e => { state.filters.q = e.target.value; renderTraceList(); });
  $('[data-role="filter-review"]').addEventListener('change', e => { state.filters.review = e.target.value; renderTraceList(); });
  $('[data-role="filter-mode"]').addEventListener('change', e => { state.filters.mode = e.target.value; renderTraceList(); });
  $('[data-role="filter-errors"]').addEventListener('change', e => { state.filters.errorsOnly = e.target.checked; renderTraceList(); });

  // trace list clicks (delegated)
  $('[data-role="trace-list"]').addEventListener('click', e => {
    const row = e.target.closest('[data-trace]');
    if (row) selectTrace(row.dataset.trace);
  });
  $('[data-role="trace-list"]').addEventListener('keydown', e => {
    const row = e.target.closest('[data-trace]');
    if (row && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); selectTrace(row.dataset.trace); }
  });

  // tree clicks (delegated): caret toggles, row selects
  $('[data-role="span-tree"]').addEventListener('click', e => {
    const caret = e.target.closest('[data-caret]');
    if (caret) {
      e.stopPropagation();
      const id = caret.dataset.caret;
      state.collapsed.has(id) ? state.collapsed.delete(id) : state.collapsed.add(id);
      renderTree();
      return;
    }
    const row = e.target.closest('[data-span]');
    if (row) selectSpan(row.dataset.span);
  });
  $('[data-role="span-tree"]').addEventListener('keydown', e => {
    const row = e.target.closest('[data-span]');
    if (row && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); selectSpan(row.dataset.span); }
  });

  // annotation autosave
  $('[data-role="annot-mode"]').addEventListener('change', persistAnnotation);
  let noteTimer = null;
  $('[data-role="annot-note"]').addEventListener('input', () => {
    clearTimeout(noteTimer);
    noteTimer = setTimeout(persistAnnotation, 600);
  });

  // export
  $('[data-role="export-json"]').addEventListener('click', exportJSON);
  $('[data-role="export-csv"]').addEventListener('click', exportCSV);

  // expose a few internals for automated tests
  window.__tv = { state, parseUpload, setData, filteredTraces, annotationRows };
}

init();
